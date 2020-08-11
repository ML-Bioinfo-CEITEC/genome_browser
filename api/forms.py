from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    #TODO remove validators? can be empty
    chromozom = StringField('chromozom')
    protein_name = StringField('protein name', validators=[DataRequired()])
    submit = SubmitField('search')
