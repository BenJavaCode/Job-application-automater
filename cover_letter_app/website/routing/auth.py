from flask_login import logout_user, login_required
from flask import Blueprint, render_template, redirect, url_for
from .response_managing import synchronous_flash

from ..form_classes.auth_forms import SignupForm, LoginForm
from ..services.user_service import sign_up_user, login

auth = Blueprint('auth', __name__)


# Syncronize return payloads {message:{'message':'message_text', 'category':'category_type'}, 'payload':'payload'}
# {message:{'message_text':'', 'category':''}, 'payload':''}
# Make it so that a view, will always only call 1 service.
# The view function will always get a response back of the same format
# It is therefore the responsibility of a route function to know how to deal with the response.

# Synchronous
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    
    form = SignupForm()
    
    if form.validate_on_submit():
        # Response object
        responsebody = sign_up_user(
                       username=form.username.data, 
                       email=form.email.data, 
                       password=form.password.data, 
                       confirm_password=form.password_confirm.data
                       ) 
        # Flash message of responsebody
        synchronous_flash(responsebody)
        # Action based on status of request
        if responsebody['message']['category'] == 'success':   
            return redirect(url_for('home.homepage'))
        
    return render_template('sign_up.html', form=form)
        


@auth.route('/login', methods=['GET', 'POST'])
def login_():
    form = LoginForm()
    if form.validate_on_submit(): 
        responsebody = login(email=form.email.data, password=form.password.data)
        synchronous_flash(responsebody)
        if responsebody['message']['category'] == 'success':
            return redirect(url_for('home.homepage'))
    return render_template('login.html', form=form)



@auth.route('/logout')
@login_required
def logout_():
    logout_user()
    return redirect(url_for('home.homepage'))

