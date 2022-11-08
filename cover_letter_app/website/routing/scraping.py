from flask_login import login_required
from flask import Blueprint, render_template, jsonify, redirect, url_for

from ..services.service_handlers import responsebody as create_responsebody
from ..services.competence_service import get_sets_by_type, get_competences_by_set_id
from ..services.jobpost_service import execute_query, set_jobpost_status_to_removed
from ..services.cover_letter_service import create_cl, create_prompt

from ..form_classes.jobpost_forms import *
from ..form_classes.scrapingquery_forms import QuerySelectorForm
from .response_managing import populate_query_selector, synchronous_flash

scraper = Blueprint('scraping', __name__)

ERROR_RESPONSEBODY = create_responsebody(success=False, message_text='Something went wrong')

def populate_prompt_form(create_prompt_form):
    # Populate form from users sets.
    skillsets_options = [(competenceset.id, competenceset.name) for competenceset in get_sets_by_type(1)['payload']]
    create_prompt_form.skillset_selector.choices.extend(skillsets_options) 
    motivationset_options = [(competenceset.id, competenceset.name) for competenceset in get_sets_by_type(2)['payload']]
    create_prompt_form.motivationset_selector.choices.extend(motivationset_options) 
    
#Synchronous
@scraper.route('/scraping', methods=['GET'])
@login_required
def scraping():
    query_selector_form = QuerySelectorForm()
    create_prompt_form = PromptForm()
    remove_jobpost_form = RemoveJobpostForm()
    create_cl_form = CreateCoverLetterForm()
    
    populate_query_selector(query_selector_form)
    populate_prompt_form(create_prompt_form)
    
    return render_template(template_name_or_list='scraping.html',
                           query_selector_form=query_selector_form,
                           create_prompt_form=create_prompt_form,
                           remove_jobpost_form=remove_jobpost_form,
                           jobpost=[],
                           create_cl_form=create_cl_form,
                           )
    


#Synchronous
@scraper.route('/scraping', methods=['POST'])
@login_required
def get_jobposts():
    
    query_selector_form = QuerySelectorForm()
    create_prompt_form = PromptForm() 
    remove_jobpost_form = RemoveJobpostForm()
    create_cl_form = CreateCoverLetterForm()
    
    populate_query_selector(query_selector_form)
    populate_prompt_form(create_prompt_form)
    
    if query_selector_form.validate_on_submit():
        
        scrapingquery_id = query_selector_form.options.data 
        responsebody = execute_query(scrapingquery_id)

        if responsebody['message']['category'] == 'success':
            return render_template(
                           template_name_or_list='scraping.html',
                           query_selector_form=query_selector_form,
                           create_prompt_form=create_prompt_form,
                           create_cl_form=create_cl_form,
                           jobposts=responsebody['payload'],
                           number_jobposts=len(responsebody['payload']),
                           remove_jobpost_form=remove_jobpost_form
                           )
        else: 
            synchronous_flash(responsebody)
            return redirect(url_for('scraping.scraping'))
     
 
# Asynchronous
@scraper.route('/discard_jobpost', methods=['POST'])
@login_required
def change_jobpost_status():
    remove_jobpost_form = RemoveJobpostForm()
    if remove_jobpost_form.validate_on_submit():
        responsebody = set_jobpost_status_to_removed(remove_jobpost_form.jobpost_id.data)
        return jsonify(responsebody)
    else:
        return jsonify(ERROR_RESPONSEBODY)
        
#Asynchronous
@scraper.route('/create_prompt', methods=['POST'])
@login_required
def create_prompt_():
    
    create_prompt_form = PromptForm() 
    populate_prompt_form(create_prompt_form)
    skillset_id, motivationset_id = create_prompt_form.skillset_selector.data, create_prompt_form.motivationset_selector.data
    
    if create_prompt_form.validate_on_submit() and skillset_id != -1 and motivationset_id != -1:

        #Get skills and motivation from their sets
        responsebody_skills = get_competences_by_set_id(skillset_id)
        responsebody_motivations = get_competences_by_set_id(motivationset_id)
        
        # Exchange list of competence objects with list of dict representation
        if responsebody_skills['message']['category'] == 'success' and responsebody_motivations['message']['category'] == 'success':
            skills = [{'id': competence.id, 'text': competence.text } 
                                              for competence in responsebody_skills['payload']]
            motivations = [{'id': competence.id, 'text': competence.text } 
                                                   for competence in responsebody_motivations['payload']]
        else:
            return jsonify(ERROR_RESPONSEBODY)
        
        job_info = create_prompt_form.job_info.data
        responsebody = create_prompt({'skills':skills, 'motivations':motivations, 'job_info':job_info})
        
        return jsonify(responsebody)
    else:
        return jsonify(create_responsebody(success=False, message_text='You need to choose skillset and motivationset'))

        
     
#Asynchronous
@scraper.route('/create_cl', methods=['POST'])
@login_required
def create_cl_():
    create_cl_form = CreateCoverLetterForm()
    if create_cl_form.validate_on_submit():
        responsebody = create_cl(prompt=create_cl_form.prompt.data, 
                                 temperature=create_cl_form.temperature.data,
                                 top_p=create_cl_form.top_p.data, 
                                 frequency_penalty=create_cl_form.frequency_penalty.data,
                                 presence_penalty=create_cl_form.presence_penalty.data
                                 )
        return jsonify(responsebody)
    else:
        return jsonify(ERROR_RESPONSEBODY)


    

