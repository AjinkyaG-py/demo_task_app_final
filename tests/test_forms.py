import pytest
from flask import Flask

from app.authentication.forms.login_form import LoginForm
from app.techpub_leads.forms.approve_book import ApproveBookForm as TPApproveBookForm
from app.techpub_leads.forms.add_books import BookDetailsForm
from app.techpub_leads.forms.project_details import ProjectDetailsForm
from app.writers.forms.move_book_to_next_stage import MoveBookToNextStageForm
from app.writers.forms.book_transfer import BookTransferForm
from app.development_leads.forms.approve_book import ApproveBookForm as DevApproveBookForm


def test_login_form_instantiation():
    app = Flask(__name__)
    app.config["WTF_I18N_ENABLED"] = False
    with app.app_context():
        f = LoginForm(meta={"csrf": False})
        assert hasattr(f, "email") and hasattr(f, "password")


def test_techpub_approve_form_instantiation():
    app = Flask(__name__)
    app.config["WTF_I18N_ENABLED"] = False
    with app.app_context():
        f = TPApproveBookForm(meta={"csrf": False})
        assert hasattr(f, "submit")


def test_book_details_form_instantiation():
    app = Flask(__name__)
    app.config["WTF_I18N_ENABLED"] = False
    with app.app_context():
        f = BookDetailsForm(meta={"csrf": False})
        assert hasattr(f, "book_number") and hasattr(f, "writer")


def test_project_details_form_instantiation():
    app = Flask(__name__)
    app.config["WTF_I18N_ENABLED"] = False
    with app.app_context():
        f = ProjectDetailsForm(meta={"csrf": False})
        assert hasattr(f, "project_name") and hasattr(f, "techpub_manager")


def test_move_book_to_next_stage_form_instantiation():
    app = Flask(__name__)
    app.config["WTF_I18N_ENABLED"] = False
    with app.app_context():
        f = MoveBookToNextStageForm(meta={"csrf": False})
        assert hasattr(f, "stage_name") and hasattr(f, "reviewer_names")


def test_book_transfer_form_instantiation():
    app = Flask(__name__)
    app.config["WTF_I18N_ENABLED"] = False
    with app.app_context():
        f = BookTransferForm(meta={"csrf": False})
        assert hasattr(f, "writer_name")


def test_development_approve_form_instantiation():
    app = Flask(__name__)
    app.config["WTF_I18N_ENABLED"] = False
    with app.app_context():
        f = DevApproveBookForm(meta={"csrf": False})
        assert hasattr(f, "submit")
