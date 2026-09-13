from app import db
from datetime import datetime


class Movements(db.Model):
    __tablename__ = "movements"


    movement_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer,db.ForeignKey("books.book_id"))
    stage_id = db.Column(db.Integer,db.ForeignKey("stages.stage_id"), default = "1")
    user_id = db.Column(db.Integer,db.ForeignKey("users.user_id"))
    techpubreviewer_id = db.Column(db.Integer, db.ForeignKey("techpub_leads.reviewer_id"))
    devreviewer_id = db.Column(db.Integer, db.ForeignKey("development_leads.dev_id"))
    date = db.Column(db.Date,default = datetime.utcnow())
    approved = db.Column(db.String(10), default = None)
    comments = db.Column(db.String(200))
    
    book = db.relationship("Books")
    stage = db.relationship("Stages")
    user = db.relationship("Users")
    techpub_reviewer = db.relationship("Techpub_Leads")
    dev_reviewer = db.relationship("Development_Leads")