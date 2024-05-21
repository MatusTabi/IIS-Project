from init import db
from sqlalchemy import Time

class Departures(db.Model):
    __tablename__ = 'departures'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_name = db.Column(db.String(10), db.ForeignKey('trafficline.line_name'), nullable=False)
    stop_name = db.Column(db.String(50), db.ForeignKey('stop.name'), nullable=False)
    time = db.Column(Time)
    order_number = db.Column(db.Integer, default=1)
    direction = db.Column(db.Boolean, default=False)
    
    trafficLine = db.relationship('TrafficLine', backref=db.backref('departures', lazy=True, cascade='all, delete-orphan'))
    stop = db.relationship('Stop', backref=db.backref('departures', lazy=True, cascade='all, delete-orphan'))
    