from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or Config)


    login_manager.init_app(app)
    # Where to redirect for login-required pages (blueprint.endpoint)
    login_manager.login_view = 'login_page.home'

    from app.authentication.view import login_page
    app.register_blueprint(login_page)

    from app.techpub_leads.views import techpub_leads_bp
    app.register_blueprint(techpub_leads_bp)

    from app.writers.views import writers_bp
    app.register_blueprint(writers_bp)

    from app.development_leads.views import dev_leads_bp
    app.register_blueprint(dev_leads_bp)

    from app.models.projects import Projects
    from app.models.writers import Users
    from app.models.books import Books
    from app.models.movements import Movements
    from app.models.techpub_leads import Techpub_Leads
    from app.models.stages import Stages
    from app.models.reviewers import Reviewers
    from app.models.dev_leads import Development_Leads


    db.init_app(app)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.writers import Users
    from app.models.techpub_leads import Techpub_Leads
    from app.models.dev_leads import Development_Leads
    # Expect `user_id` to be prefixed with the model type (e.g. "users-3", "techpub-2", "dev-4").
    # This avoids id collisions across the different user tables.
    if not user_id:
        return None

    prefix = None
    id_part = user_id
    if isinstance(user_id, str) and '-' in user_id:
        prefix, id_part = user_id.split('-', 1)

    try:
        pk = int(id_part)
    except (TypeError, ValueError):
        return None

    # If a prefix is present, query the corresponding table first.
    if prefix == 'users':
        return Users.query.get(pk)
    if prefix == 'techpub':
        return Techpub_Leads.query.get(pk)
    if prefix == 'dev':
        return Development_Leads.query.get(pk)

    # Backwards-compatibility: no prefix — try all tables in a sensible order.
    user = Users.query.get(pk)
    if user:
        return user
    user = Techpub_Leads.query.get(pk)
    if user:
        return user
    return Development_Leads.query.get(pk)