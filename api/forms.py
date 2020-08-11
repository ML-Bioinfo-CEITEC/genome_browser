from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional

class SearchForm(FlaskForm):
    #TODO remove validators? can be empty
    chromozom = StringField('chromozom')
    # protein_name = StringField('protein name', validators=[DataRequired()])
    protein_name = StringField('protein name')
    sort_by = SelectField('sort by', choices=["score", "protein_name"], default="protein_name")
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
