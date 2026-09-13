from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class Development_Leads(db.Model,UserMixin):
    
    __tablename__ = "development_leads"
    
    dev_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(200))
    email = db.Column(db.String(50))
    
    def get_id(self):
        return f"dev-{self.dev_id}"
    
    def check_password(self,password):
        return check_password_hash(self.password,password)