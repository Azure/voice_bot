import os
import time
import sounddevice as sd
import numpy as np
import azure.cognitiveservices.speech as speechsdk
import wave
from pydub import AudioSegment
from utils.config_defaults import get_language_code
from utils.logger import log_event

monitoring = True
human_speaking = False
last_speech_time = time.time()

from dotenv import load_dotenv
load_dotenv(override=True)
speech_ep = os.getenv('SPEECH_EP')
speech_key = os.getenv('SPEECH_KEY')
speech_region = os.getenv('SPEECH_REGION')

human_audio_segment = None

def get_human_response(language, update_callback=None):
    global text, monitoring, last_speech_time, human_audio_segment
    monitoring = True
    last_speech_time = time.time()

    human_text = []
    human_audio_segment = AudioSegment.empty()

    lang = get_language_code(language)


    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    stream = speechsdk.audio.PushAudioInputStream()
    audio_config = speechsdk.audio.AudioConfig(stream=stream)
    speech_recognizer = speechsdk.SpeechRecognizer(language=lang, speech_config=speech_config, audio_config=audio_config)

    def handle_recognizing(evt):
        global human_speaking, last_speech_time
        human_speaking = True
        last_speech_time = time.time()  # Reset the timer
        print(human_speaking, evt.result.text)
        try:
            if update_callback:
                update_callback(evt.result.text)
                print("Calling updating callback with ", evt.result.text)
        except Exception as e:
            print(e)

    def handle_recognized(evt):
        global human_speaking, text, last_speech_time, monitoring
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            human_text.append(evt.result.text)
            log_event("Speech Transcribed")
            try:
                if update_callback:
                    update_callback(' '.join(human_text))
                    print("Calling update callback with ", evt.result.text)
            except Exception as e:
                print(e)
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('NOMATCH: Speech could not be recognized.')
        
        # Stop monitoring after recognition
        human_speaking = False
        monitoring = False
        print(f"Recognized: {human_speaking} {evt.result.text}")

    def handle_canceled(evt):
        print('CANCELED: {}'.format(evt))
        if evt.reason == speechsdk.CancellationReason.Error:
            print('CANCELED: Error details - {}'.format(evt.error_details))
        speech_recognizer.stop_continuous_recognition()
        monitoring = False

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(handle_recognizing)
    speech_recognizer.recognized.connect(handle_recognized)
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED: {}'.format(evt)))
    speech_recognizer.canceled.connect(handle_canceled)

    

    # Function to start the transcription process
    def start_transcription():
        global monitoring, last_speech_time
        global human_audio_segment
        last_speech_time = time.time()  # Reset the timer
        # Start continuous speech recognition
        log_event("Start Human Speech Recognition")
        speech_recognizer.start_continuous_recognition_async()

        
        # Callback function to push audio data to the stream
        def audio_callback(indata, frames, time1, status):
            global human_audio_segment
            log_event("Push audio to stream")
            stream.write(indata.tobytes())
            audio_array = np.frombuffer(indata, dtype=np.int16)
            new_segment = AudioSegment(
                audio_array.tobytes(),
                frame_rate=16000,
                sample_width=2,  
                channels=1
            )
            human_audio_segment += new_segment

            
        # Start recording from the microphone
        try:
            with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=audio_callback):
                print("Recording... Press Ctrl+C to stop.")
                while monitoring:
                    if time.time() - last_speech_time > 3:
                        print("No speech detected for 3 seconds, stopping transcription.")
                        monitoring = False
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("Recording stopped.")
        finally:
            stream.close()
            speech_recognizer.stop_continuous_recognition()

    # Function to detect if the user starts speaking
    def detect_speech(indata, frames, time1, status):
        global human_speaking, last_speech_time
        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm > 0.2:  # Threshold for detecting speech
            print("Speech detected, starting transcription...")
            sd.stop()
            human_speaking = True
            last_speech_time = time.time()  # Reset the timer
            start_transcription()

    # Monitor the microphone input to detect speech
    try:
        with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=detect_speech):
            print("Monitoring microphone... Start speaking to begin transcription.")
            while monitoring:
                if time.time() - last_speech_time > 5 and not human_speaking:
                    print("No speech detected for 5 seconds, stopping monitoring.")
                    monitoring = False
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Monitoring stopped.")

    return ' '.join(human_text), human_audio_segment

