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
import time

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

#spk_sig = [-0.891684, -0.130390, 1.368452, 0.209146, -0.008386, 0.731464, 0.856996, 0.177553, 1.316603, 1.637085, -0.343187, 0.312126, -0.743909, 0.739855, -1.235087, 0.763318, 2.273797, -1.281516, 0.633055, -0.363363, -0.357788, 0.798039, 2.180442, 0.073130, -1.248862, 0.907360, 1.057549, -0.422057, -0.223189, -0.628476, -0.225164, 0.772648, 0.048056, -0.942278, -0.931837, -1.090142, 0.144348, 0.087319, 0.221830, 0.665487, 0.254930, 0.269606, 2.065293, -1.073388, -0.571818, 0.210244, -0.229996, -0.781241, -0.249673, 0.015498, 0.661528, 0.598963, -2.868980, -0.995247, 0.010761, 0.401485, 0.294723, 1.188548, -0.692303, -1.621983, 0.707475, 1.241550, -1.892505, -0.050193, -1.430929, 0.176586, -1.172653, 0.981032, -0.745509, 1.914016, 1.173026, -1.093171, -0.363510, 2.389551, -0.379826, -0.164128, -1.401292, -2.165837, -0.146951, 0.701714, 0.134839, -0.346942, 1.262309, 0.616360, -0.485776, -1.527874, -0.019630, 1.045032, -1.120039, 2.957704, 0.252245, 1.071884, -0.470590, 1.534587, -0.025618, 0.026857, 0.765317, 0.321612, -1.029844, 0.131316, -1.619612, 0.091628, -0.575747, -0.531433, 1.625027, 0.165951, 0.238775, 0.173136, 0.271162, 0.837523, -0.629695, -0.748469, 1.368035, -0.490642, 1.784966, 1.125934, -1.143485, -0.026725, 0.939180, -0.984909, -0.480827, 0.256497, -0.678360, 0.933805, 0.178494, 0.795298, -1.261258, 0.943654]
spk_sig = [-0.701766, 0.313454, 0.285104, -1.157942, -1.025656, 0.359487, -0.397543, -0.738973, 1.633481, -0.077619, 0.011297, -0.023481, -0.990958, -0.921590, -0.902737, -0.254562, 0.478593, 0.081016, 2.043904, 0.215783, -0.296242, 2.049364, 1.969494, -0.381765, -1.040035, -0.636572, -0.671292, -1.647781, 0.562115, 0.728833, -0.559134, -1.370062, 0.188702, -1.041054, 0.293849, -2.449665, 1.236091, 1.086694, -0.957984, 0.546023, 0.734656, 1.330279, 0.438040, 0.081506, -0.930533, 1.371469, 0.052700, -0.599288, 0.187568, 0.868085, 0.107612, 0.932629, 0.196172, 1.043293, -0.365125, 0.157180, 0.250023, -0.250561, -0.656860, -1.249357, 0.954533, 0.354545, 0.005050, -1.438345, -0.137508, -0.992737, -0.565105, 0.281953, -1.195023, 2.748891, -0.586424, -2.366060, -0.605496, -0.659102, 0.303107, 0.115082, -1.137468, -0.366137, -0.188624, -1.305033, 0.387655, -1.230271, -0.223709, -0.165224, -0.592402, -0.331704, 0.071005, 1.486784, 0.599618, -0.233855, 0.503320, -0.620836, -0.224790, 0.052773, -0.929046, 0.081823, -0.366624, -1.166075, 0.810104, 2.258941, 0.908314, -0.301767, -0.180385, -1.584045, -0.037256, -1.478272, 0.285490, -1.095387, -0.696070, -0.104534, -1.608816, 0.968370, 1.192020, -1.002699, 2.961337, 0.216760, -0.145203, 1.073298, -0.002436, -0.253612, 0.700424, 1.986816, -1.314074, 1.693625, 0.702341, 1.354820, -2.112917, 0.155190]
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
    

def process_chunk(rec, message):
    if message == '{"eof" : 1}':
        #print('Final RESULT')
        #print(rec.FinalResult())
        return rec.FinalResult()
    if rec.AcceptWaveform(message):
        # res = json.loads(rec.Result())
        # if 'spk' in res:
        #     print(cosine_dist(spk_sig,res['spk']))
        #print(rec.Result())
        #print('Printed')
        return rec.Result()
    else:
        return rec.PartialResult()


class KaldiTask:
    def __init__(self, user_connection):
        self.__resampler = AudioResampler(format='s16', layout='mono', rate=16000) #16000
        self.__pc = user_connection
        self.__audio_task = None
        self.__track = None
        self.__channel = None
        self.__recognizer = KaldiRecognizer(model, 16000)
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
        curr_time = time.time()
        while True:  #when start is pressed
            frame = await self.__track.recv() 
            #print(frame)
            #print(len(frame.split('/')))
            temp_message = frame.planes[0].to_bytes()
            #print(len(str(temp_message).split('\\')))
            #print('After resampling')
            frame = self.__resampler.resample(frame) #resampled to 48khz
            #print(len(str(frame).split("\\")))
            #print(frame)
            max_frames_len = 8000 #max buffer size trial and test
            message = frame.planes[0].to_bytes() 
            #print(len(str(message).split('\\')))
            recv_frames = bytearray(message)
            #print(len(recv_frames),'recv')
            dataframes += recv_frames 
            #print(len(dataframes),'df')
            if len(dataframes) > max_frames_len:
                now_time = time.time()
                #print(now_time - curr_time,'TIME')
                curr_time = now_time
                wave_bytes = bytes(dataframes)
                #speaker = await self.loop.run_in_executor(pool, find_speaker, self.__recognizer, wave_bytes)
                response = await self.loop.run_in_executor(pool, process_chunk, self.__recognizer, wave_bytes)
                #response = json.loads(response)
                #response['spk'] = speaker
                #response = json.dumps(response)
                print(response)
                #print(speaker)
                #print('-----')
                self.__channel.send(response)
                # if speaker is not None:
                #     self.__channel.send(speaker)
                dataframes = bytearray(b"") #buffer freed

            #print(len(str(frame).split("\\")))
            #print()

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
