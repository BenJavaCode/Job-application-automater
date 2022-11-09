from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators, EmailField
from flask_wtf import FlaskForm


class SignupForm(FlaskForm):
    username = StringField("Username", [validators.InputRequired()])
  
    email = EmailField("Enter email", [validators.InputRequired()])
  
    password = PasswordField("Password", [validators.InputRequired(), 
                            validators.Length(min=6)
                            ])
  
    password_confirm = PasswordField("Confirm password", [validators.InputRequired(), validators.Length(min=6)])
  
    user_agreement = BooleanField("terms of service", [validators.DataRequired()])
  
    submit = SubmitField()
    
    
class LoginForm(FlaskForm):
    email = EmailField("Email", [validators.InputRequired()])
    password = PasswordField("Password", [validators.InputRequired()])
    