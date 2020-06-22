from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, SelectMultipleField, BooleanField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length

class ChecklistForm(FlaskForm):
    title = StringField('Checklist title:', validators=[
                        DataRequired(), Length(max=140)])
    description = StringField('Checklist description:', validators=[
                              DataRequired(), Length(max=250)])
    submit = SubmitField('Save checklist')

class ChecklistItemForm(FlaskForm):
    title = StringField('Item title:', validators=[
                        DataRequired(), Length(max=140)])
    description = StringField('Checklist item description:', validators=[
                              DataRequired(), Length(max=250)])
    submit = SubmitField('Save checklist item')
