from init import db

class TrafficLine(db.Model):
    __tablename__ = 'trafficline'
    line_name = db.Column(db.String(10), primary_key=True)
    starting_stop = db.Column(db.String(50), db.ForeignKey('stop.name'))
    last_stop = db.Column(db.String(50), db.ForeignKey('stop.name'))
