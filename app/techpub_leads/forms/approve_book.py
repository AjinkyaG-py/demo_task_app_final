from flask_wtf import FlaskForm
from wtforms import SubmitField


class ApproveBookForm(FlaskForm):
    submit = SubmitField("Approve")
