from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField

class BookDetailsForm(FlaskForm):
    writer_choices = [
        ("Ajinkya Godbole", "Ajinkya Godbole"),
        ("Michael Curry", "Michael Curry")]
    book_number = StringField("Book Number")
    revision = StringField("Revision")
    writer = SelectField("Writer", choices=writer_choices)
    submit = SubmitField("Submit") 