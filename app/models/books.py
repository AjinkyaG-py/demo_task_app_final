from app import db
from enum import Enum

class BookStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Books(db.Model):
    __tablename__ = "books"
    
    book_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    book_number = db.Column(db.String(50))
    revision = db.Column(db.String(3))
    writer = db.Column(db.String(30), nullable = False)
    project_name = db.Column(db.String(50))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id"))
    book_status = db.Column(db.String(30), default = 'open')
    
    project = db.relationship("Projects")