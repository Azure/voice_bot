import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
translater_key = os.getenv("TRANSLATOR_KEY")
translater_region = os.getenv("TRANSLATOR_REGION")

def translate_text(text, from_language, to_language):
    global translater_key, translater_region
    # Define the API URL for translation with dynamic parameters for from and to languages
    url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from={from_language}&to={to_language}"

    # Set headers including the subscription key and other required details
    headers = {
        "Ocp-Apim-Subscription-Key": translater_key,  # API subscription key
        "Ocp-Apim-Subscription-Region": translater_region,  # Specify the region of your subscription
        "Content-Type": "application/json",  # Set content type to JSON
        "X-ClientTraceId": "875030C7-5380-40B8-8A03-63DACCF69C11"  # Unique ID for debugging
    }

    # Prepare the JSON payload with the text to translate
    data = [
        {
            "text": text
        }
    ]

    # Send the POST request to the API with the payload
    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the translated text from the response
        result = response.json()
        translated_text = result[0]['translations'][0]['text']
        return translated_text
    else:
        # Handle the error by returning the status code and message
        return f"Error: {response.status_code} - {response.text}"

