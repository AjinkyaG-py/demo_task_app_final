import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

DB_NAME = "demo_task_app.db"
SQLITE_DB_PATH = os.path.join(base_dir, DB_NAME)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

DATABASE_URI = f"sqlite:///{SQLITE_DB_PATH}"

class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = SECRET_KEY