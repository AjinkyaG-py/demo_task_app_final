from app import db


class Stages(db.Model):
    
    __tablename__ = "stages"
    
    stage_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    stage_name = db.Column(db.String(80))
    
    def get_stage_id(self,stage_name):
        query = db.session.query(Stages.stage_id).filter(Stages.stage_name == stage_name)
        stg_id = db.session.scalar(query)
        
        return stg_id