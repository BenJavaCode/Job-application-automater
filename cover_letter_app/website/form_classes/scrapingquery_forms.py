from wtforms import StringField, validators, SelectField, IntegerField, RadioField, SelectMultipleField, FieldList
from wtforms import Form, FormField


from flask_wtf import FlaskForm

from wtforms import widgets

from configurations.config import GEOGRAPHIES

AGE_CHOICES = [(-1, 'All')] + [(0,'1'),(1,'2'),(2,'3'),(3,'4'),(4,'5'),(5,'6'),(6,'7'),(7,'14'),(8,'30')]
CATEGORIES = [('none', 'All'), ('Informationsteknologi', 'Informationsteknologi'), ('Ingeniør', 'Ingeniør'), 
              ('Ledelse', 'Ledelse'), ('Handel og service', 'Handel og service'), ('Salg og kommunikation', 'Salg og kommunikation'),
              ('Undervisning', 'Undervisning'), ('Kontor og økonomi', 'Kontor og økonomi'), 
              ('Social og sundhed', 'Social og sundhed'), ('Øvrige stillinger', 'Øvrige stillinger')]
GEOS = [(i+1, geo) for i,geo in enumerate(GEOGRAPHIES)]                            



# This code from WTForms docs, this class changes the way SelectMultipleField
# is rendered by jinja
# https://wtforms.readthedocs.io/en/3.0.x/specific_problems/
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    
class QuerySelectorForm(FlaskForm):
    options = SelectField(coerce=int, choices=[(-1, '-- Create new --')])
    
     
class CreateQueryForm(FlaskForm):
    scrapingquery_id = IntegerField(validators=[validators.InputRequired()], default=-1)
    
    name = StringField('Name', validators=[validators.InputRequired()])
    
    age = SelectField('Maximun age of jobs', choices=AGE_CHOICES, coerce=int, default=-1, validators=[validators.InputRequired()])
    
    category = SelectField('Job Categories', choices=CATEGORIES, coerce=str, default=-1, validators=[validators.InputRequired()])
    
    geographies = MultiCheckboxField('Area', choices=GEOS, coerce=int)
    
    # This is basicly a dicttionary string. and must be manually checked, to see if any fufu is going on
    criterias = StringField()   
    
    
    


    
    
    
    
   
