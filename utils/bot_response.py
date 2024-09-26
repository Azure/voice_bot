import os
import asyncio

from utils.human_response import human_speaking
from utils.aoai_response import get_openai_streaming_response

from utils.text_audio import text_to_speech_streaming, init_synthesizer
from utils.audio_queue import process_queue

from utils.logger import log_event

from dotenv import load_dotenv
load_dotenv(override=True)


async def get_bot_response(chat_history, persona, language, blnPersonalVoice):
    
    completion = await get_openai_streaming_response(chat_history)

    init_synthesizer(language, persona)

    queue = asyncio.Queue()
    processing_task = asyncio.create_task(process_queue(queue))

    tasks = []
    

    text_buffer = ""
    all_text = ""
    
    def process_text_buffer(text_buffer, all_text):
        task = text_to_speech_streaming(text_buffer.strip(), queue, language, blnPersonalVoice)
        tasks.append(asyncio.create_task(task))
        
        all_text += text_buffer
        text_buffer = "" 
        return text_buffer, all_text

    for event in completion:
        if human_speaking:
            await queue.put(None)
            break;
        if len(event.choices) > 0:
            
            for choice in event.choices:
                if choice.delta.content and len(choice.delta.content) > 0:
                    
                    text_buffer += choice.delta.content
                    if any(p in text_buffer for p in ",;.!?"):  
                        log_event("OpenAI Response chunk with punctuation")
                        text_buffer, all_text = process_text_buffer(text_buffer, all_text)
                        
     
    if not human_speaking and text_buffer.strip(): 
        log_event("OpenAI Response chunk Final")
        text_buffer, all_text = process_text_buffer(text_buffer, all_text)

    await asyncio.gather(*tasks)
     # Signal the end of the queue
    await queue.put(None) 
    await processing_task
    
    return all_text
   


