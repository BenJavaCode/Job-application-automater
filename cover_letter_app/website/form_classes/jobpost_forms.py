from email.policy import default
from wtforms import validators, SelectField, TextAreaField, IntegerField, FloatField
from flask_wtf import FlaskForm

     
    
class PromptForm(FlaskForm):
    # Default choice?
    job_info = TextAreaField("Paste the jobpost here", [validators.InputRequired()])
    skillset_selector = SelectField(coerce=int, choices=[(-1, '-- Select Set --')])
    motivationset_selector = SelectField(coerce=int, choices=[(-1, '-- Select Set --')])

    
class RemoveJobpostForm(FlaskForm):
    jobpost_id = IntegerField([validators.InputRequired()])
    
class CreateCoverLetterForm(FlaskForm):
    prompt = TextAreaField([validators.InputRequired()])
    temperature = FloatField("Temperature: Controls randomness",[validators.InputRequired(), 
                                                    validators.NumberRange(min=0.0, max=1.0)], default=0.85) 
    top_p = FloatField("Top_p: Controls diversity via nucleus sampling",[validators.InputRequired(), 
                                                    validators.NumberRange(min=0.0, max=1.0)], default=1.0)
    frequency_penalty = FloatField("Frequency_penalty: A higher number penalized repetition of words",[validators.InputRequired(), 
                                                    validators.NumberRange(min=0.0, max=1.0)], default=0.2)
    presence_penalty = FloatField("Presence_penalty: A higher number penalized repetition of subjects",[validators.InputRequired(), 
                                                    validators.NumberRange(min=0.0, max=1.0)], default=0.35)
    
    