from init import db

class Stop(db.Model):
    __tablename__ = 'stop'
    name = db.Column(db.String(50), primary_key=True)
