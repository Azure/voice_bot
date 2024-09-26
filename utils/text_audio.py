from utils.cls_push_audio_stream import stream_writer
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
import asyncio
from utils.config_defaults import get_default_voice
from utils.config_defaults import get_personal_voice

from utils.logger import log_event


load_dotenv(override=True)


speech_ep = os.getenv('SPEECH_EP')
speech_key = os.getenv('SPEECH_KEY')
speech_region = os.getenv('SPEECH_REGION')

synthesizer = None
speech_config = None
audio_config = None
push_stream = None



def init_synthesizer(language, persona):
    global synthesizer
    global speech_config
    global audio_config
    global push_stream
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm)
    push_stream = speechsdk.audio.PushAudioOutputStream(stream_writer)
    audio_config = speechsdk.audio.AudioOutputConfig(stream=push_stream)
    speech_config.speech_synthesis_voice_name = get_default_voice(language, persona)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


async def text_to_speech_streaming(text, queue, language, blnPersonalVoice):
    log_event("Start Text to Speech")
    loop = asyncio.get_event_loop()
    if language=="English":
        locale = "en-US"
    else:
        locale = "hi-IN"
    if blnPersonalVoice:
        speaker_profile_id = get_personal_voice()
        
        ssml = "<speak version='1.0' xml:lang='hi-IN' xmlns='http://www.w3.org/2001/10/synthesis' " \
       "xmlns:mstts='http://www.w3.org/2001/mstts'>" \
       "<voice name='DragonLatestNeural'>" \
       "<mstts:ttsembedding speakerProfileId='%s'/>" \
       "<mstts:express-as style='cheerful' styledegree='5'>" \
       "<lang xml:lang='%s'> %s </lang>" \
       "</mstts:express-as>" \
       "</voice></speak> " % (speaker_profile_id, locale, text)
        result_future = synthesizer.speak_ssml_async(ssml)
    else:
        result_future = synthesizer.speak_text_async(text)
    
    result = await loop.run_in_executor(None, result_future.get)

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")
        audio_segment = stream_writer.get_audio_segment()
        await queue.put(audio_segment)
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")