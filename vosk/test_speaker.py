#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SpkModel
import sys
import wave
import json
import os
import numpy as np

model_path = "model"
spk_model_path = "model-spk"

if not os.path.exists(model_path):
    print ("Please download the model from https://alphacephei.com/vosk/models and unpack as {} in the current folder.".format(model_path))
    exit (1)

if not os.path.exists(spk_model_path):
    print ("Please download the speaker model from https://alphacephei.com/vosk/models and unpack as {} in the current folder.".format(spk_model_path))
    exit (1)

wf = wave.open(sys.argv[1], "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print ("Audio file must be WAV format mono PCM.")
    exit (1)

# Large vocabulary free form recognition
model = Model(model_path)
spk_model = SpkModel(spk_model_path)
#rec = KaldiRecognizer(model, wf.getframerate(), spk_model)
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetSpkModel(spk_model)

# We compare speakers with cosine distance. We can keep one or several fingerprints for the speaker in a database
# to distingusih among users.
#spk_sig = [-1.110417,0.09703002,1.35658,0.7798632,-0.305457,-0.339204,0.6186931,-0.4521213,0.3982236,-0.004530723,0.7651616,0.6500852,-0.6664245,0.1361499,0.1358056,-0.2887807,-0.1280468,-0.8208137,-1.620276,-0.4628615,0.7870904,-0.105754,0.9739769,-0.3258137,-0.7322628,-0.6212429,-0.5531687,-0.7796484,0.7035915,1.056094,-0.4941756,-0.6521456,-0.2238328,-0.003737517,0.2165709,1.200186,-0.7737719,0.492015,1.16058,0.6135428,-0.7183084,0.3153541,0.3458071,-1.418189,-0.9624157,0.4168292,-1.627305,0.2742135,-0.6166027,0.1962581,-0.6406527,0.4372789,-0.4296024,0.4898657,-0.9531326,-0.2945702,0.7879696,-1.517101,-0.9344181,-0.5049928,-0.005040941,-0.4637912,0.8223695,-1.079849,0.8871287,-0.9732434,-0.5548235,1.879138,-1.452064,-0.1975368,1.55047,0.5941782,-0.52897,1.368219,0.6782904,1.202505,-0.9256122,-0.9718158,-0.9570228,-0.5563112,-1.19049,-1.167985,2.606804,-2.261825,0.01340385,0.2526799,-1.125458,-1.575991,-0.363153,0.3270262,1.485984,-1.769565,1.541829,0.7293826,0.1743717,-0.4759418,1.523451,-2.487134,-1.824067,-0.626367,0.7448186,-1.425648,0.3524166,-0.9903384,3.339342,0.4563958,-0.2876643,1.521635,0.9508078,-0.1398541,0.3867955,-0.7550205,0.6568405,0.09419366,-1.583935,1.306094,-0.3501927,0.1794427,-0.3768163,0.9683866,-0.2442541,-1.696921,-1.8056,-0.6803037,-1.842043,0.3069353,0.9070363,-0.486526]
spk_sig = [-0.86216, 0.800802, 0.305077, 1.018946, 0.332992, 0.728345, 0.22177, -0.057331, -0.312422, -0.18903, 2.15433, -1.040895, -0.324892, -0.040285, -0.070632, 1.740796, -0.906863, 0.555349, 0.792185, -1.112543, -0.902351, -0.091858, -0.228827, -1.476363, -1.3917, 0.495772, -1.467199, -0.547215, 0.889568, 0.088187, 0.103688, -0.073738, -0.368249, -0.092607, -0.844306, -1.568685, -0.420665, 0.835872, -0.502208, 0.14659, -0.035979, 2.10606, 0.99805, -1.141984, -1.862036, -0.323849, -0.789557, -0.627814, 0.796999, -1.602665, 0.103011, -0.256812, -1.022917, -1.567891, -0.849196, -0.685688, 0.967585, -0.159438, 0.545183, 0.148485, -0.156379, 0.057301, 0.799321, 0.129315, 0.493416, -1.101013, -2.374983, 0.518266, -0.933343, -0.425307, 0.943059, 1.01415, -0.595508, 0.787108, 1.374999, 0.951322, -1.377733, -2.667694, 1.189639, 0.855436, 0.861312, -2.754208, 0.981956, -0.504542, -0.494619, -0.22519, -1.288385, 0.05072, -1.177311, 2.106066, -1.936133, -0.298182, 0.984004, -0.974334, -1.462997, -0.81532, 0.806968, -1.454142, 0.379467, 1.11662, -0.854579, -2.388636, -1.149753, -0.140828, -0.598622, 0.783878, 1.073628, -0.395649, -0.69955, -0.376798, -0.370349, 0.918835, 0.599873, -1.736887, 1.238875, 0.119234, 1.793961, -0.458078, -0.940023, 0.501722, -0.058763, -0.066067, -0.169399, -0.882527, -1.104013, -0.070096, 0.195085, -0.08364]
def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())
        print ("Text:", res['text'])
        if 'spk' in res:
            print ("X-vector:", res['spk'])
            print('-'*80)
            print ("Speaker distance:", cosine_dist(spk_sig, res['spk']), "based on", res['spk_frames'], "frames")
            print('-'*80)
            #spk_sig = res['spk']
            

print ("Note that second distance is not very reliable because utterance is too short. Utterances longer than 4 seconds give better xvector")

res = json.loads(rec.FinalResult())
print ("Text:", res['text'])
if 'spk' in res:
    print ("X-vector:", res['spk'])
    print('-'*80)
    print ("Speaker distance:", cosine_dist(spk_sig, res['spk']), "based on", res['spk_frames'], "frames")
    if cosine_dist(spk_sig,res['spk']) < 0.5:
        print('Same speaker')
    else:
        print('Different speaker')
    print('-'*80)
