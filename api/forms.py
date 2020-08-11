from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    #TODO remove validators? can be empty
    chromozom = StringField('chromozom')
    protein_name = StringField('protein name', validators=[DataRequired()])
    sort_by = StringField('sort by')
    # area_min = IntegerField('area min')
    # area_max = IntegerField('area max')

    submit = SubmitField('search')
