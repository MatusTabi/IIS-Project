from init import db

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
    ticketID = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(32), db.ForeignKey('vehicles.vin'))
    engineer = db.Column(db.Integer)
    moderator = db.Column(db.Integer)
    date = db.Column(db.Date)
    request = db.Column(db.String(1024))
    report = db.Column(db.String(1024))
    state = db.Column(db.String(50))
    