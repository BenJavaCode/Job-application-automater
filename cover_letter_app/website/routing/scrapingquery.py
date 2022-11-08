from random import choices
from flask_login import login_required
from flask import Blueprint, render_template, jsonify, redirect, url_for

from ..form_classes.scrapingquery_forms import *
from ..services.user_service import current_user_repr
from ..services.scraping_query_service import get_queries, get_query, create_query, update_query
from .response_managing import synchronous_flash, populate_query_selector

scrapingquery = Blueprint('scrapingquery', __name__)



#Synchronous
@scrapingquery.route('/queries', methods=['GET'])
@login_required
def scrapingqueries():
    query_selector_form = QuerySelectorForm()
    create_query_form = CreateQueryForm()
    populate_query_selector(query_selector_form)
    
    user_rep = current_user_repr()['payload']
    
    return render_template(template_name_or_list='queries.html',
                           user=user_rep,
                           query_selector_form=query_selector_form,
                           create_query_form=create_query_form)



#Synchronous 
@scrapingquery.route('/update_or_create_query', methods=['POST'])
@login_required
def create_or_update_query():
    create_query_form = CreateQueryForm()
    
    if create_query_form.validate_on_submit(): 
        # Create new       
        if create_query_form.scrapingquery_id.data == -1: 
            responsebody = create_query(
                            name=create_query_form.name.data,
                            age=create_query_form.age.data,
                            category=create_query_form.category.data,
                            geographies=create_query_form.geographies.data,
                            criterias=create_query_form.criterias.data
                            )
        else: 
            # Update existing
            responsebody = update_query(
                            id=create_query_form.scrapingquery_id.data,
                            name=create_query_form.name.data,
                            age=create_query_form.age.data,
                            category=create_query_form.category.data,
                            geographies=create_query_form.geographies.data,
                            criterias=create_query_form.criterias.data
                            )
            
        synchronous_flash(responsebody)
    return redirect(url_for('scrapingquery.scrapingqueries'))
    
    
#Asynchronous
@scrapingquery.route('/get_query_data', methods=['POST'])
@login_required
def get_query_data():
    """_summary_:
       Populate query data forms with selected scrapingquery

    Returns:
        _type_: All data of selected Scrapingquery_service. 
            If the selected option is 'Create New'=-1. Then all data will be None.
    """
    query_selector_form = QuerySelectorForm()
    populate_query_selector(query_selector_form)

    
    if query_selector_form.validate_on_submit():
        id = query_selector_form.options.data
        responsebody = get_query(id)
        
        if responsebody['payload'] is None:
            responsebody['payload'] = -1
            
        elif responsebody['message']['category'] == 'success':
            query = responsebody['payload']
            responsebody['payload'] = {'id': query.id, 
                                        'name': query.name, 
                                        'age': query.age,
                                        'category': query.category, 
                                        'criterias': str(query.criterias).split(','),
                                        'geographies': [geo.id for geo in query.geographies]
                                        }
        return jsonify(responsebody)
    
    
