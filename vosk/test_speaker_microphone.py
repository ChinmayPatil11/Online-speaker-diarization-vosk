#!/usr/bin/env python3

import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
from vosk import Model, KaldiRecognizer, SpkModel
import wave
import json
import os
import numpy as np

#spk_sig = [-1.110417,0.09703002,1.35658,0.7798632,-0.305457,-0.339204,0.6186931,-0.4521213,0.3982236,-0.004530723,0.7651616,0.6500852,-0.6664245,0.1361499,0.1358056,-0.2887807,-0.1280468,-0.8208137,-1.620276,-0.4628615,0.7870904,-0.105754,0.9739769,-0.3258137,-0.7322628,-0.6212429,-0.5531687,-0.7796484,0.7035915,1.056094,-0.4941756,-0.6521456,-0.2238328,-0.003737517,0.2165709,1.200186,-0.7737719,0.492015,1.16058,0.6135428,-0.7183084,0.3153541,0.3458071,-1.418189,-0.9624157,0.4168292,-1.627305,0.2742135,-0.6166027,0.1962581,-0.6406527,0.4372789,-0.4296024,0.4898657,-0.9531326,-0.2945702,0.7879696,-1.517101,-0.9344181,-0.5049928,-0.005040941,-0.4637912,0.8223695,-1.079849,0.8871287,-0.9732434,-0.5548235,1.879138,-1.452064,-0.1975368,1.55047,0.5941782,-0.52897,1.368219,0.6782904,1.202505,-0.9256122,-0.9718158,-0.9570228,-0.5563112,-1.19049,-1.167985,2.606804,-2.261825,0.01340385,0.2526799,-1.125458,-1.575991,-0.363153,0.3270262,1.485984,-1.769565,1.541829,0.7293826,0.1743717,-0.4759418,1.523451,-2.487134,-1.824067,-0.626367,0.7448186,-1.425648,0.3524166,-0.9903384,3.339342,0.4563958,-0.2876643,1.521635,0.9508078,-0.1398541,0.3867955,-0.7550205,0.6568405,0.09419366,-1.583935,1.306094,-0.3501927,0.1794427,-0.3768163,0.9683866,-0.2442541,-1.696921,-1.8056,-0.6803037,-1.842043,0.3069353,0.9070363,-0.486526]
spk_sig = [-0.773389, -0.73717, 1.275487, -0.487569, -2.135169, -0.783545, 0.283837, -0.018334, 0.43941, 0.67484, -0.393122, -0.002782, 0.43808, 0.098184, 0.165732, 0.583729, 1.673824, 1.088284, 0.43474, 1.034753, -0.796987, 0.697885, -0.040288, -1.199373, -0.037404, -1.548899, -0.106753, -1.335022, -0.928976, 0.942514, 1.613167, 1.815215, 0.810201, 0.276238, -1.546976, -0.535832, 1.290188, 1.639523, -0.268406, 1.240504, -0.845258, 1.716153, 1.369405, -0.25914, 0.642708, -0.643677, -0.61306, -1.107061, 0.190344, 1.314819, -0.985385, -0.531921, -1.813758, -0.372912, 0.257205, -1.522812, 0.972665, -0.202797, -0.345997, -2.311688, -0.849789, 1.897015, 0.018081, -0.669031, 0.272256, -2.552338, -0.921482, 0.461005, -0.919727, -0.816862, 1.194907, -0.479275, 0.045081, 0.710327, -0.743397, 1.358062, -0.683101, -0.222206, 0.087818, 0.842219, 0.551095, -0.238619, 0.042113, 1.416729, -1.022528, 0.545019, -1.074623, 0.774204, -0.349728, 0.557254, -2.345414, 0.363452, -1.559706, 0.847072, -0.233011, 0.492974, 0.026915, -0.584113, -1.435716, 0.230675, -0.436398, -1.567772, 0.212944, -0.469766, -0.909639, -1.359021, 0.985728, -0.110336, -1.289395, -0.384932, -1.223847, 0.201405, 0.480435, -0.105438, 2.191668, -0.691559, 0.150652, 0.098956, -2.287292, 0.819728, 1.488051, 0.702594, 1.01435, 0.396382, -0.001635, 0.766398, 0.105405, 1.728893]

def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)

q = queue.Queue()
trans = open('text.txt','w')
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-m', '--model', type=str, metavar='MODEL_PATH',
    help='Path to the model')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

try:
    if args.model is None:
        args.model = "model"
    if not os.path.exists(args.model):
        print ("Please download a model for your language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(args.model)
    spk_model = vosk.SpkModel("model-spk")

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                            channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            rec.SetSpkModel(spk_model)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    #print(rec.Result())
                    res = json.loads(rec.Result())
                    print(res)
                    #print('-----',type(res['text']))
                    #trans.write(res['text']+'\n')
                    if 'spk' in res:
                        print('-'*80)
                        #trans.write(res['text'])
                        #print ("Speaker distance:", cosine_dist(spk_sig, res['spk']), "based on", res['spk_frames'], "frames")
                        if cosine_dist(spk_sig,res['spk']) < 0.5:
                            print('Same person')
                            trans.write('speaker-1:' + res['text'] + '\n')
                        else:
                            print('Different Person')
                            trans.write('speaker-2:' + res['text'] + '\n')
                        print('-'*80)
                        spk_sig = res['spk']

                else:
                    print(rec.PartialResult())
                if dump_fn is not None:
                    dump_fn.write(data)

except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
