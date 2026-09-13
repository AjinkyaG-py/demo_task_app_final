from app import db

class Projects(db.Model):
    __tablename__ = "projects"
    
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    network_id = db.Column(db.String(20))
    project_name = db.Column(db.String(50))
    product_line = db.Column(db.String(50))
    development_manager = db.Column(db.String(50), nullable=True)
    techpub_manager = db.Column(db.String(50))