
import os
from utils.config_defaults import get_summary_prompt
from utils.aoai_response import get_openai_response

def get_conv_summary(language, conv_msgs):
    
    summary_prompt = get_summary_prompt(language)
   
    # Concatenating all conversation content
    user_content = ''
    for entry in conv_msgs[1:]:
        role = entry["role"]
        content = entry["content"].replace("'","")
        user_content += f"{role}:{content}\n "

    # Creating the user role entry with concatenated content
    user_role = {'role': 'user', 'content': user_content.strip()}

    # Creating the final array
    system_summary_role = {'role': 'system', 'content': summary_prompt}
    final_array = [system_summary_role, user_role]
    print(user_role)
    response = get_openai_response(final_array)
    print(response)
    return response
    
    