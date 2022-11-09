from wtforms import SubmitField, StringField, PasswordField, validators, EmailField, SelectField, IntegerField

from flask_wtf import FlaskForm

class PasswordForm(FlaskForm):
    current_password = PasswordField("Current password", [validators.InputRequired()])
    new_password = PasswordField("New password", [validators.InputRequired(), validators.Length(min=6)])
    confirm_password = PasswordField("Confirm password", [validators.InputRequired(), validators.Length(min=6)])
    submit = SubmitField('Register')
    
class EmailForm(FlaskForm):
    email = EmailField("New Email", [validators.InputRequired()])
    submit = SubmitField('Register')
    
class UsernameForm(FlaskForm):
    username = StringField("New Username", [validators.InputRequired()])
    submit = SubmitField('Register')
    
class EducationForm(FlaskForm):
    eduback = StringField("Educational background (used to generate CL)", [validators.InputRequired(), validators.Length(max=250)])

class RealNameForm(FlaskForm):
    real_name = StringField("Full name (used to generate CL)",[validators.InputRequired(), validators.Length(max=250)])
    
class CreateQueryForm(FlaskForm):
    query_name = StringField("Name of new Query", [validators.InputRequired()])
    # Use one below
    
class CreateSetForm(FlaskForm):
    name = StringField("Desired Name", [validators.InputRequired()])
    set_type = IntegerField([validators.InputRequired(), validators.AnyOf(values=[1,2])])
    
class CreateCompetenceForm(FlaskForm):
    text = StringField([validators.InputRequired()])
    competenceset_id = IntegerField([validators.InputRequired()])
    
class ChildSelector(FlaskForm):
    parent_id = IntegerField(validators.InputRequired())
    options = SelectField(u'Group', coerce=int, choices=[(-1, '--Select Set--')], default=-1)
    #parent_id = IntegerField([validators.InputRequired()]) This would be the user?
    

class TypeSelector(FlaskForm):
    options = SelectField('Skill', choices=[(1,'Skillset'), (2,'Motivationset')], coerce=int, default=1)
  

class deleteCompetenceForm(FlaskForm):
    id_container = IntegerField('somethin', [validators.InputRequired()])
    
    
    
