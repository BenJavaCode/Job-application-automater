from ..persistence.dao import user_dao
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user
from .service_handlers import request_handler, responsebody

"""_summary_:
    User services, that either query or manipulate data in User object model.
    used primarily by routing layer, but also by other services.
"""

@request_handler
def update_password(current_password, new_password, confirm_password):
    if __check_password_correct(current_password):
        if new_password == confirm_password:
            enc_password = generate_password_hash(new_password)
            user_dao.update_current_user(password=enc_password)
            return responsebody(message_text='Password succesfully updated', success=True)
        else: return responsebody(message_text='Passwords do not match', success=False)
    else: return responsebody(message_text='Password not correct', success=False)
    
@request_handler
def update_username(username):
    if __check_username(username):
        user_dao.update_current_user(username=username)
        return responsebody(message_text=f'Username changed to {username}', success=True)
    else: 
        return responsebody(message_text='Username already taken', success=False)

@request_handler   
def update_email(email):
    if __check_email(email):
        email = str(email).lower()
        user_dao.update_current_user(email=email)
        return responsebody(message_text=f'Email changed to {email}', success=True)
    else: 
        return responsebody(message_text='Email used in another account', success=False)

# Very verbose error messages, not good for security.
@request_handler    
def sign_up_user(password, confirm_password, username, email):
    if __check_username(username):
        if __check_email(email):
            email = str(email).lower()
            if password == confirm_password:
                enc_password = generate_password_hash(password)
                new_user = user_dao.create_new(username=username,
                                                email=email,
                                                password=enc_password)
                user_dao.save(new_user)
                login_user(new_user, remember=True)
                return responsebody(message_text='User succesfully created', success=True)
            else: return responsebody(message_text='Passwords do not match', success=False)
        else: return responsebody(message_text='Email already in use', success=False)
    else: return responsebody(message_text='Username already in use', success=False)
    
@request_handler  
def login(password, email):
    user = user_dao.get_first_where(email=email)
    if user:
        if __check_password_correct(specified_password=password, user=user):
            login_user(user, remember=True)
            return responsebody(message_text='Logged in', success=True)
        else: return responsebody(message_text='Password incorrect', success=False)
    else: return responsebody(message_text='User does not exist', success=False)
    
@request_handler
def current_user_repr(exclude=['password']):
    user_repr = user_dao.current_user_repr()
    if exclude:
        user_repr = {key:val for (key,val) in user_repr.items() if key not in exclude}
        return responsebody(success=True, payload=user_repr)
    return responsebody(success=True, payload=user_repr)

@request_handler
def change_educational_background(education_string):
    user_dao.update_current_user(education=education_string)
    return responsebody(message_text=f'Educational background changed to {education_string}', success=True)

@request_handler
def change_real_name(real_name_string):
    user_dao.update_current_user(real_name=real_name_string)
    return responsebody(message_text=f'Name changed to {real_name_string}', success=True)


# Used by cover letter service   
def get_real_name():
    return user_dao.get_user_attr('real_name')

# Used by cover letter service
def get_education():
    return user_dao.get_user_attr('education')

def __check_password_correct(specified_password, user=False):
    if user: 
        password = user.password
    else: 
        password = user_dao.get_user_attr('password')
    return check_password_hash(password, specified_password)

"""_summary_:
Returns true if the provided username is not already in use.
Else it returns false.
"""
def __check_username(new_username):
    if user_dao.get_first_where(username=new_username):
        return False
    else: 
        return True
    
"""_summary_:
Returns true if the provided email is not already in use.
Else it returns false.
"""
def __check_email(new_email):
    if user_dao.get_first_where(email=new_email):
        return False
    else: 
        return True
    