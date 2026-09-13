from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class BookTransferForm(FlaskForm):
    writer_name = StringField("Transfer to:")
    submit = SubmitField("Submit")