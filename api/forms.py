from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional

class SearchForm(FlaskForm):
    #TODO remove validators? can be empty
    chromozom = StringField('chromozom')
    # protein_name = StringField('protein name', validators=[DataRequired()])
    protein_name = StringField('protein name')
    sort_by = SelectField('sort by', choices=["score_desc","score_asc", "protein_name_desc", "protein_name_asc"])
    area_min = IntegerField('binding location min',
            validators=[
                Optional()
            ]
        )
    area_max = IntegerField('binding location max',
            validators=[
                Optional()
            ]
        )
    loc_min = IntegerField('gene location min',
            validators=[
                Optional()
            ]
        )
    loc_max = IntegerField('gene location max',
            validators=[
                Optional()
            ]
        )

    submit = SubmitField('search')
