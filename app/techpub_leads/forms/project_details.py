from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class ProjectDetailsForm(FlaskForm):
    techpub_manager_choices = [
        ("Gail Baragar", "Gail Baragar")]
    development_manager_choices = [('David M', 'David M')]
    network_id = StringField("Network ID")
    project_name = StringField("Project Name")
    product_line = StringField("Product Line")
    development_manager = SelectField("Development Manager",choices = development_manager_choices)
    techpub_manager = SelectField("Technical Publication Manager",choices = techpub_manager_choices)
    submit = SubmitField("Submit")