from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField


class MoveBookToNextStageForm(FlaskForm):
    stage_name = SelectField(
        "Stage Name",
        choices=[
            ("Draft Content", "Draft Content"),
            ("Internal Review", "Internal Review"),
            ("External Review", "External Review"),
            ("Release", "Release"),
        ],
    )
    reviewer_names = SelectField("Enter Reviewers (comma-separated):", choices=[])
    comments = TextAreaField("Comments")
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set reviewer choices based on the selected stage at runtime
        if self.stage_name.data == "Internal Review":
            self.reviewer_names.choices = [("Gail Baragar", "Gail Baragar")]
        elif self.stage_name.data == "External Review":
            self.reviewer_names.choices = [("David M", "David M")]
        else:
            self.reviewer_names.choices = [("", "No reviewer required")]