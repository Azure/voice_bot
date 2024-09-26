from pydub import AudioSegment

import asyncio
import simpleaudio as sa

from utils.logger import log_event

final_segment = AudioSegment.empty()
  
def play_audio(audio_segment):
    log_event("Start Playing audio")
    play_obj = sa.play_buffer(audio_segment.raw_data, audio_segment.channels, audio_segment.sample_width, audio_segment.frame_rate)
    play_obj.wait_done() 
    log_event("End Playing audio")
              
async def process_queue(queue):
    global final_segment
    while True:
        audio_segment = await queue.get()
        if audio_segment is None:
            break
        await asyncio.to_thread(play_audio, audio_segment)
        final_segment += audio_segment


def get_final_segment(in_segment=None):
    global final_segment
    if in_segment:
        final_segment += in_segment
    return final_segment