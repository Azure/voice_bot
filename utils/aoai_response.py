from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from utils.logger import log_event

load_dotenv(override=True)

open_ai_endpoint = os.getenv("OPEN_AI_ENDPOINT")
open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_deployment_name = os.getenv("OPEN_AI_DEPLOYMENT_NAME")
api_version = "2024-02-15-preview"

def create_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=open_ai_key,  # key
        azure_endpoint=open_ai_endpoint,  # gpt4
        api_version=api_version,  # ver
    )

client = create_openai_client()

async def get_openai_streaming_response(messages):
    #print("Message Text:", message_text)
    completion = client.chat.completions.create(
            model=open_ai_deployment_name,
            messages=messages,
            temperature=0,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            stream=True
        )
    return completion

def get_openai_response(messages):
    completion = client.chat.completions.create(
            model=open_ai_deployment_name,
            messages=messages,
            temperature=0,
            max_tokens=4000,
            top_p=0.95,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            stream=False
        )
    
    log_event("OpenAI Response")
    return completion.choices[0].message.content