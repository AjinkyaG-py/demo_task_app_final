from app import db



class Reviewers(db.Model):
    __tablename__ = "reviewers"
    
    rm_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30))

    def get_rm_ids(self,usernames):
        
        list_of_ids = []
        for username in usernames:
            query = db.session.query(Reviewers.rm_id).filter(Reviewers.username == username)
            rev_id = db.session.scalar(query)
            list_of_ids.append(rev_id)
        
        return list_of_ids