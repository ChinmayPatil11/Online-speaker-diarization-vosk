# Online-speaker-diarization-vosk

### Models used
- model: https://alphacephei.com/vosk/models vosk-model-en-us-0.22  
- model-spk: https://alphacephei.com/vosk/models vosk-model-spk-0.4 (Speaker Identification model)

### To create spk_sig (speaker signature)
- Create an audio file of your voice atleast 4 seconds long. Should be wav format and mono PCM.
- Use script /vosk/create_spk_sig.py to generate speaker signature.
  - python create_spk_sig.py (path_to_wav_file
- Copy the spk_sig to /vosk/test_microphone_speaker.py.
- Run test_microphone_speaker.py
  - python test_microphone_speaker.py
- Conversation is transcribed to text.txt
