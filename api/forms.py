from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField
from wtforms.validators import DataRequired, Optional

class SearchForm(FlaskForm):
    #TODO remove validators? can be empty
    chromozom = StringField('chromozom')
    protein_name = StringField('protein name', validators=[DataRequired()])
    sort_by = StringField('sort by')
    area_min = IntegerField('area min',
            validators=[
                Optional()
            ]
        )
    area_max = IntegerField('area max',
            validators=[
                Optional()
            ]
        )

    submit = SubmitField('search')
