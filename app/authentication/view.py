from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.authentication.forms.login_form import LoginForm
from app.models.dev_leads import Development_Leads
from app.models.techpub_leads import Techpub_Leads
from app.models.writers import Users
from flask_login import current_user, login_user, logout_user, LoginManager
from app import db


login_page = Blueprint('login_page', __name__, template_folder='templates')


def _redirect_to_role_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login_page.home'))

    user_obj = current_user._get_current_object()

    if isinstance(user_obj, Users):
        return redirect(url_for('writers.landing'))

    if isinstance(user_obj, Techpub_Leads):
        return redirect(url_for('techpub_leads.landing'))

    if isinstance(user_obj, Development_Leads):
        return redirect(url_for('development_leads.landing'))

    return redirect(url_for('login_page.home'))

@login_page.route('/', methods=['GET', 'POST'])
def home():

    if current_user.is_authenticated:
        return _redirect_to_role_dashboard()

    login_form = LoginForm()

    if login_form.validate_on_submit():

        username = login_form.email.data
        print("Username:", username)
        password = login_form.password.data


        user = db.session.query(Users).filter_by(email=username).first()


        if user and user.check_password(password):
            login_user(user)

            return _redirect_to_role_dashboard()

        Techpub_Lead = db.session.query(Techpub_Leads).filter_by(email=username).first()

        if Techpub_Lead and Techpub_Lead.check_password(password):
            login_user(Techpub_Lead)
            return _redirect_to_role_dashboard()

        dev_lead = db.session.query(Development_Leads).filter_by(email=username).first()
        if dev_lead and dev_lead.check_password(password):
            login_user(dev_lead)
            return _redirect_to_role_dashboard()

    return render_template('home.html', login_form=login_form)

@login_required
@login_page.route('/landing', methods=['GET','POST'])
def landing(user=None):
    return _redirect_to_role_dashboard()

@login_page.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out!", 'success')
    return redirect(url_for('login_page.home'))