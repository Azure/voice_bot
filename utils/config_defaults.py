import json
from utils.translated_text import translate_text

with open('config.json') as f:
        config = json.load(f)

def get_default_prompts(theme, language):
    prompts = config["conversation_prompts"]
    if theme in prompts.keys():
        bot_prompt = prompts[theme]["bot"]
        human_prompt = prompts[theme]["human"]
    else:
        bot_prompt = ""
        human_prompt = ""
    if language != "English":
        supported_languages = config["supported_languages"]
        from_lang, to_lang = supported_languages["English"], supported_languages[language]
        bot_prompt = translate_text(bot_prompt, from_lang, to_lang)
        human_prompt = translate_text(human_prompt, from_lang, to_lang)
    return bot_prompt, human_prompt

def get_language_code(language):
    supported_languages = config["supported_languages"]
    if language in supported_languages.keys():
        return supported_languages[language]
    else:
        return supported_languages["English"]
    
def get_supported_languages():
    return config["supported_languages"].keys()

def get_supported_themes():
    return config["conversation_prompts"].keys()    

def get_default_voice(language, persona):
    voices = config["voices"]
    if language in voices.keys():
        voice = voices[language]
    else:
        voice = voices["English"]
    print(voice)
    print(voice[persona])
    return voice[persona]


def get_summary_prompt(language):
    summary_prompt = config["summary_prompt"]
    if language != "English":
        supported_languages = config["supported_languages"]
        from_lang, to_lang = supported_languages["English"], supported_languages[language]
        summary_prompt = translate_text(summary_prompt, from_lang, to_lang)
    return summary_prompt

def get_personal_voice():
    return config["personal_voice"]

