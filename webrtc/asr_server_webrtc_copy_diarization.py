#!/usr/bin/env python3
#https://singerlinks.com/2021/08/how-to-transcribe-a-podcast-to-text-for-free/
#https://github.com/ideasman42/nerd-dictation/blob/master/nerd-dictation
import json
import logging
import ssl
import sys
import os
import concurrent.futures
import asyncio
from xmlrpc.client import ResponseError
import numpy as np
from pathlib import Path
from typing import final
from vosk import KaldiRecognizer, Model, SpkModel
from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable
from aiortc import RTCSessionDescription, RTCPeerConnection
from av.audio.resampler import AudioResampler

ROOT = Path(__file__).parent

vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', '0.0.0.0')
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 2700))
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', 'model')
vosk_sample_rate = float(os.environ.get('VOSK_SAMPLE_RATE', 8000))
vosk_cert_file = os.environ.get('VOSK_CERT_FILE', None)

model = Model(vosk_model_path)
spk_model = SpkModel("model-spk")

pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))
loop = asyncio.get_event_loop()

spk_sig = [-0.891684, -0.130390, 1.368452, 0.209146, -0.008386, 0.731464, 0.856996, 0.177553, 1.316603, 1.637085, -0.343187, 0.312126, -0.743909, 0.739855, -1.235087, 0.763318, 2.273797, -1.281516, 0.633055, -0.363363, -0.357788, 0.798039, 2.180442, 0.073130, -1.248862, 0.907360, 1.057549, -0.422057, -0.223189, -0.628476, -0.225164, 0.772648, 0.048056, -0.942278, -0.931837, -1.090142, 0.144348, 0.087319, 0.221830, 0.665487, 0.254930, 0.269606, 2.065293, -1.073388, -0.571818, 0.210244, -0.229996, -0.781241, -0.249673, 0.015498, 0.661528, 0.598963, -2.868980, -0.995247, 0.010761, 0.401485, 0.294723, 1.188548, -0.692303, -1.621983, 0.707475, 1.241550, -1.892505, -0.050193, -1.430929, 0.176586, -1.172653, 0.981032, -0.745509, 1.914016, 1.173026, -1.093171, -0.363510, 2.389551, -0.379826, -0.164128, -1.401292, -2.165837, -0.146951, 0.701714, 0.134839, -0.346942, 1.262309, 0.616360, -0.485776, -1.527874, -0.019630, 1.045032, -1.120039, 2.957704, 0.252245, 1.071884, -0.470590, 1.534587, -0.025618, 0.026857, 0.765317, 0.321612, -1.029844, 0.131316, -1.619612, 0.091628, -0.575747, -0.531433, 1.625027, 0.165951, 0.238775, 0.173136, 0.271162, 0.837523, -0.629695, -0.748469, 1.368035, -0.490642, 1.784966, 1.125934, -1.143485, -0.026725, 0.939180, -0.984909, -0.480827, 0.256497, -0.678360, 0.933805, 0.178494, 0.795298, -1.261258, 0.943654]
def cosine_dist(x,y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx,ny) / np.linalg.norm(nx) / np.linalg.norm(ny)

def find_speaker(rec, message):
    #print(message)
    if message == '{"eof" : 1}':
        return rec.FinalResult()
    if rec.AcceptWaveform(message):
        res = json.loads(rec.Result())
        if 'spk' in res:
            if cosine_dist(spk_sig,res['spk']) < 0.6:
                print('---recognised---')
                return 'Chinmay'
            else:
                print('---recognised---')
                return 'Person'
        else:
            print('UNIDENTIFIED')

def process_chunk(rec, message):
    if message == '{"eof" : 1}':
        return rec.FinalResult()
    if rec.AcceptWaveform(message):
        # res = json.loads(rec.Result())
        # if 'spk' in res:
        #     print(cosine_dist(spk_sig,res['spk']))
        return rec.Result()
    else:
        return rec.PartialResult()


class KaldiTask:
    def __init__(self, user_connection):
        self.__resampler = AudioResampler(format='s16', layout='mono', rate=48000)
        self.__pc = user_connection
        self.__audio_task = None
        self.__track = None
        self.__channel = None
        self.__recognizer = KaldiRecognizer(model, 48000)
        self.__recognizer.SetSpkModel(spk_model)
        self.loop = asyncio.get_event_loop()


    async def set_audio_track(self, track):
        self.__track = track

    async def set_text_channel(self, channel):
        self.__channel = channel

    async def start(self):
        self.__audio_task = asyncio.create_task(self.__run_audio_xfer())

    async def stop(self):
        if self.__audio_task is not None:
            self.__audio_task.cancel()
            self.__audio_task = None

    async def __run_audio_xfer(self):
        dataframes = bytearray(b"")
        while True:
            frame = await self.__track.recv()
            frame = self.__resampler.resample(frame)
            max_frames_len = 8000
            message = frame.planes[0].to_bytes()
            recv_frames = bytearray(message)
            dataframes += recv_frames
            if len(dataframes) > max_frames_len:
                wave_bytes = bytes(dataframes)
                speaker = await self.loop.run_in_executor(pool, find_speaker, self.__recognizer, wave_bytes)
                response = await self.loop.run_in_executor(pool, process_chunk, self.__recognizer, wave_bytes)
                response = json.loads(response)
                response['spk'] = speaker
                response = json.dumps(response)
                print(response)
                print(speaker)
                print('-----')
                self.__channel.send(response)
                # if speaker is not None:
                #     self.__channel.send(speaker)
                dataframes = bytearray(b"")

async def index(request):
    content = open(str(ROOT / 'static' / 'index_copy.html')).read()
    return web.Response(content_type='text/html', text=content)


async def offer(request):
    #print('request:',request)
    params = await request.json()
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type'])
    #print(params['sdp'], params['type'], params)
    pc = RTCPeerConnection()
    #print('pc',pc)
    kaldi = KaldiTask(pc)
    #print(kaldi)
    @pc.on('datachannel')
    async def on_datachannel(channel):
        #print('channel:',channel)
        await kaldi.set_text_channel(channel)
        await kaldi.start()

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == 'failed':
            await pc.close()

    @pc.on('track')
    async def on_track(track):
        if track.kind == 'audio':
            await kaldi.set_audio_track(track)

        @track.on('ended')
        async def on_ended():
            await kaldi.stop()

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)


    return web.Response(
        content_type='application/json',
        text=json.dumps({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }))


if __name__ == '__main__':

    if vosk_cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(vosk_cert_file)
    else:
        ssl_context = None

    app = web.Application()
    app.router.add_post('/offer', offer)

    app.router.add_get('/', index)
    app.router.add_static('/static/', path=ROOT / 'static', name='static')

    web.run_app(app, port=vosk_port, ssl_context=ssl_context)
