from dotenv import load_dotenv
import json
import requests
from PIL import Image as PILImage
from openai import AzureOpenAI
import os
import io

load_dotenv(override=True)
open_ai_endpoint = os.getenv("OPEN_AI_ENDPOINT")
open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_deployment_name = os.getenv("OPEN_AI_DEPLOYMENT_NAME")
open_ai_api_version = os.getenv("OPEN_AI_API_VERSION")


openai_client = AzureOpenAI(
    api_key=open_ai_key,  # key
    azure_endpoint=open_ai_endpoint,  # gpt4
    api_version=open_ai_api_version,  # ver
)

def gen_dalle_img(theme, persona, file_name):
    if os.path.exists(file_name):
        return file_name
    
    with open('config.json') as f:
        config = json.load(f)
    
    dalle_prompt = config[theme][persona]

    dalle_key = os.getenv("DALLE_KEY")
    dalle_ep = os.getenv("DALLE_EP")
    dalle_api_version = os.getenv("DALLE_API_VERSION")
    dalle_client = AzureOpenAI(
        api_version=dalle_api_version,
        azure_endpoint=dalle_ep,
        api_key=dalle_key
    )

    result = dalle_client.images.generate(
        model="Dalle3", 
        prompt=dalle_prompt,
        n=1
    )

    image_url = json.loads(result.model_dump_json())['data'][0]['url']
    response = requests.get(image_url)
    img_pil = PILImage.open(io.BytesIO(response.content))

    img_pil.save(file_name)


def get_open_ai_response(messages):
    completion = openai_client.chat.completions.create(
            model=open_ai_deployment_name,
            messages=messages,
            temperature=0,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            stream=False
        )
    return completion.choices[0].message.content


def gen_dalle_img_prompt(theme):
    with open('config.json') as f:
        config = json.load(f)
    
    sample_theme = list(config.keys())[0]

    sample_bot_prompt = config[sample_theme]['bot']
    sample_human_prompt = config[sample_theme]['human'] 

    system_prompt = f"""Generate a prompt for a cartoon character for a bot providing info on theme: {theme}
----------------------------
    Example prompt for theme: {sample_theme}
    {sample_bot_prompt}
    """
    user_prompt = f"Prompt for bot providing info on theme: {theme}"
    user_role = {'role': 'user', 'content': user_prompt}
    system_role = {'role': 'system', 'content': system_prompt}

    final_array = [system_role, user_role]
    bot_prompt = get_open_ai_response(final_array)

    system_prompt = f"""Generate a prompt for a for a cartoon character representing a  human looking for info on : {theme}
----------------------------
    Example prompt for theme: {sample_theme}
    {sample_human_prompt}
    """
    user_prompt = f"Prompt for human seeking info on theme: {theme}"
    user_role = {'role': 'user', 'content': user_prompt}
    system_role = {'role': 'system', 'content': system_prompt}

    final_array = [system_role, user_role]
    human_prompt = get_open_ai_response(final_array)

    #save them in config
    config[theme] = {
        'bot': bot_prompt,
        'human': human_prompt
    }
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    return bot_prompt, human_prompt


#Generate documentation for generating avatars representing bot and human for the theme

