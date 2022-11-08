from flask_login import login_required
from flask import Blueprint, render_template, jsonify, request, redirect, url_for

from ..form_classes.home_forms import *
from ..services.user_service import current_user_repr, update_email, update_password, update_username, change_real_name, change_educational_background
from ..services.competence_service import get_competences_by_set_id, get_sets_by_type, create_competence, delete_competence, create_set
from .response_managing import synchronous_flash


home = Blueprint('home', __name__)

# Synchronous   
@home.route('/', methods=['GET'])
@login_required
def homepage():

    password_form = PasswordForm()
    email_form = EmailForm()
    username_form = UsernameForm()
    education_form = EducationForm()
    real_name_form = RealNameForm()

    type_selector = TypeSelector()
    create_set_form = CreateSetForm()
    create_comp_form = CreateCompetenceForm()
    set_selector = ChildSelector()
    
    responsebody = current_user_repr()
    user_rep = responsebody['payload']
    
    return render_template(template_name_or_list='homepage.html', 
                           user=user_rep, 
                           password_form=password_form, 
                           username_form=username_form, 
                           email_form=email_form,
                           education_form=education_form,
                           real_name_form=real_name_form,
                           
                           type_selector=type_selector,
                           set_selector=set_selector, 
                           create_set_form=create_set_form,
                           create_comp_form=create_comp_form
                           )


# Synchronous   
@home.route('/change_password', methods=['POST'])
@login_required
def change_password():
    password_form = PasswordForm()
    if password_form.validate_on_submit():
        responsebody = update_password(
                    current_password=password_form.current_password.data, 
                    new_password=password_form.new_password.data,  
                    confirm_password = password_form.confirm_password.data
                    )
        synchronous_flash(responsebody)
    return redirect(url_for('home.homepage'))

        
        
# Synchronous           
@home.route('/change_username', methods=['POST'])
@login_required
def change_username():
    username_form = UsernameForm()
    if username_form.validate_on_submit():
        responsebody = update_username(username=username_form.username.data)
        synchronous_flash(responsebody)
    return redirect(url_for('home.homepage'))
       
        
# Synchronous   
@home.route('/change_email', methods=['POST'])
@login_required
def change_email():
    email_form = EmailForm()
    if email_form.validate_on_submit():
        responsebody = update_email(email=email_form.email.data)
        synchronous_flash(responsebody)
    return redirect(url_for('home.homepage'))

#Synchronous
@home.route('/change_educational_background', methods=['POST'])
@login_required
def change_education():
    education_form = EducationForm()
    if education_form.validate_on_submit():
        responsebody = change_educational_background(education_string=education_form.eduback.data)
        synchronous_flash(responsebody)
    return redirect(url_for('home.homepage'))

#Synchronous
@home.route('/change_real_name', methods=['POST'])
@login_required
def change_name():
    real_name_form = RealNameForm()
    if real_name_form.validate_on_submit():
        responsebody = change_real_name(real_name_string=real_name_form.real_name.data)
        synchronous_flash(responsebody)
    return redirect(url_for('home.homepage'))


# Asynchronous
@home.route('/get_sets', methods=['POST'])
@login_required
def get_sets():
    
    type_selector = TypeSelector()
    
    if type_selector.validate_on_submit():
        set_type = type_selector.options.data 
        responsebody = get_sets_by_type(set_type)
        # replace set objec models with representations
        if responsebody['message']['category'] == 'success':
            initial_option = [{'id':-1, 'name':'--Select Set--'}] 
            competence_rep = [{'id': competenceset.id, 'name': competenceset.name } for competenceset in responsebody['payload']]
            responsebody['payload'] = initial_option + competence_rep
        return jsonify(responsebody)
         
    return redirect(url_for('home.homepage'))

    
# Asynchronous    
@home.route('/get_competences_of_set', methods=['POST'])
@login_required
def get_competences():
    
    set_selector = ChildSelector()
    parent_id = set_selector.parent_id.data
    responsebody = get_sets_by_type(parent_id)
    # Get users sets and append them to select option
    sets = [(competenceset.id, competenceset.name) for competenceset in responsebody['payload']]
    set_selector.options.choices.extend(sets)

    if set_selector.validate_on_submit():
        id = set_selector.options.data
        responsebody = get_competences_by_set_id(id)
        # Exchange list of competence objects with list of dict representation
        if responsebody['message']['category'] == 'success':
            responsebody['payload'] = [{'id': competence.id, 'text': competence.text } for competence in responsebody['payload']]
        return jsonify(responsebody)
    return redirect(url_for('home.homepage'))
        
        
# Asynchronous
@home.route('/create_set', methods=['POST'])
@login_required
def create_set_():
    create_set_form = CreateSetForm()
    if create_set_form.validate_on_submit():
        responsebody = create_set(name=create_set_form.name.data,
                                                     set_type=create_set_form.set_type.data)
        # Exchange Set objects instance with set representation
        if responsebody['message']['category'] == 'success':
            competence_set = responsebody['payload']
            responsebody['payload'] = {'id': competence_set.id, 'name': competence_set.name}
        return jsonify(responsebody)
    return redirect(url_for('home.homepage'))
   
   
# Asynchronous   
@home.route('/create_competence', methods=['POST']) 
@login_required 
def create_competence_():
    create_comp_form = CreateCompetenceForm()
    if create_comp_form.validate_on_submit():
        responsebody = create_competence(text=create_comp_form.text.data, 
                                                            competenceset_id=create_comp_form.competenceset_id.data)
        # Exchange Competence object isntance with representation
        if responsebody['message']['category'] == 'success':
            competence = responsebody['payload']
            responsebody['payload'] = {'id':competence.id, 'text': competence.text}
        return jsonify(responsebody)
        
    return redirect(url_for('home.homepage'))

        
        
# Asynchronous         
@home.route('/delete_competence', methods=['POST'])
@login_required
def delete_competence_():
    id, competenceset_id = int(request.form.get('this_comp_id')), int(request.form.get('this_comp_set_id'))
    responsebody = delete_competence(id=id, competenceset_id=competenceset_id)
    return jsonify(responsebody)
