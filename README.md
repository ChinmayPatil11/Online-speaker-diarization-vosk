# Online-speaker-diarization-vosk

### Models used
Download the models from https://alphacephei.com/vosk/models
- model: https://alphacephei.com/vosk/models vosk-model-en-us-0.22  
  - Extract to /vosk and rename as 'model'.  
  - ![image](https://user-images.githubusercontent.com/72211393/158597195-910e953f-c84b-4ce0-8cd1-11c534d30ce5.png)

- model-spk: https://alphacephei.com/vosk/models vosk-model-spk-0.4 (Speaker Identification model)
  - Extract to /vosk and rename as 'model-spk'.  
  - ![image](https://user-images.githubusercontent.com/72211393/158597313-7fb12c4c-78f0-4d01-b420-542afe052cac.png)


### To create spk_sig (speaker signature)
##### Method 1 (Using audio file)
- Create an audio file of your voice atleast 4 seconds long. Should be wav format and mono PCM.
- Use script /vosk/create_spk_sig.py to generate speaker signature.
  - python create_spk_sig.py (path_to_wav_file)
- The speaker signature will be printed in the terminal.
- Copy the spk_sig to /vosk/test_microphone_speaker.py.

##### Method 2 (Using direct voice through microphone)
- Run /vosk/test_speaker_microphone.py
- Speaker signature will be printed in the terminal. 
- Stop the script and replace the existing signature (embedding) with the new embedding.


- Run test_microphone_speaker.py
  - python test_microphone_speaker.py
- Conversation is transcribed to text.txt
