from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Optional

class SearchForm(FlaskForm):
    chromosome = StringField('chromosome')
    protein_name = StringField('protein name')
    symbol = StringField('gene symbol')
    gene_id = StringField('ensembl gene id')
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

    score_min = FloatField('min score',
            validators=[
                Optional()
            ]
        )

    submit = SubmitField('search')
