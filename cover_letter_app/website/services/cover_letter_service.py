from .user_service import get_real_name, get_education
from .service_handlers import request_handler, responsebody
from configurations.config import OPENAI_API_KEY

import openai as ai
from googletrans import Translator


@request_handler
def create_prompt(data:dict):
    job_info = __translate_to_(data['job_info'], dest_language='en')
    full_name = get_real_name()
    education = get_education()
    prompt = __construnct_prompt(motivations=data['motivations'], skills=data['skills'],
                                        full_name=full_name, job_info=job_info, education=education)
    return responsebody(success=True, payload=prompt)

@request_handler
def create_cl(prompt, temperature, top_p, frequency_penalty, presence_penalty, dest_language='da'):
    # join.split() to remove tabs newlines and such quickly
    footer_text =" ".join("""This application was created by cover-letter automation software that utilizes webscraping, 
    data-mining, machine learning and other exciting technologies (created by myself of course).
    Link to my Github for those of you who wants to check it out: 'github link'
    """.split())
    cl_english = __create_cover_letter(prompt, temperature, top_p, frequency_penalty, presence_penalty)
    cl_container = [cl_english + ' \n \n' + footer_text, __translate_to_(cl_english, dest_language) + ' \n \n' + footer_text]
    return responsebody(success=True, payload=cl_container)


def __construnct_prompt(motivations, skills, full_name, job_info, education):

    first_name = full_name.split(' ')[0]
    motivations = ', '.join([dictionary['text'] for dictionary in motivations])
    skills = ', '.join([dictionary['text'] for dictionary in skills])

    prompt = """
    Based on a job post and information on an applicant, 
    write a truthful cover letter where you do not lie about the skills or your educational background. 
    This is the job post: {job_info}. And this is the author of this application: 
    (Name of applicant: {full_name}, Skills: {skills}. I am motivated by 
    {motivations}. I have an educational background in: {education}.
    """.format(job_info=job_info, full_name=full_name, 
                skills=skills, first_name=first_name, motivations=motivations, education=education)
    
    # Remove newlines and add newline at end.
    prompt = " ".join(prompt.split())+"\n"
    return prompt

def __translate_to_(cl_text, dest_language):
    
    trans = Translator()
    # The limit for google.api is 5000, but they change it all the time, so I have set it in anticipation
    if len(cl_text) > 4000:
        step = 4000
        chunks = [cl_text[i:i+step] for i in range(0, len(cl_text), step)]
        # Translate text chunk for chunk, as google api will block you otherwise.
        return ' '.join([trans.translate(chunk, dest=dest_language).text for chunk in chunks])
    else:
        return trans.translate(cl_text, dest=dest_language).text


def __create_cover_letter(prompt, temperature=0.85, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.35):
    
    ai.api_key = OPENAI_API_KEY # Your secret key to OpenAi
 
    response = ai.Completion.create(
        engine = "text-davinci-002", # Most capable model ATM
        prompt=prompt, # The prompt to the model
        max_tokens=2500, # maximun character with input+output
        temperature=temperature,
        top_p=top_p, # range 0-1
        n=1, # number of predictions to generate
        frequency_penalty=frequency_penalty, # A higher value increases the models chance to not repeat topics. range:0-1
        presence_penalty=presence_penalty # A higher value increases the models chance to talk about new topics range:0-1
    )

    return response['choices'][0]['text']