import openai as ai
from configurations.config import OPENAI_API_KEY


def create_cover_letter(prompt, temperature=0.85, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.35):
    
    ai.api_key = OPENAI_API_KEY # Your secret key to OpenAi
 
    response = ai.Completion.create(
        engine = "text-davinci-002",
        prompt=prompt, # The prompt to the model
        max_tokens=2500, # maximun character with input+output
        temperature=temperature,
        top_p=top_p, # range 0-1
        n=1, # number of predictions to generate
        frequency_penalty=frequency_penalty, # A higher value increases the models chance to not repeat topics. range:0-1
        presence_penalty=presence_penalty # A higher value increases the models chance to talk about new topics range:0-1
    )

    text = response['choices'][0]['text']
    return text