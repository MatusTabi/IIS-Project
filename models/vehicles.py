from init import db

class Vehicles(db.Model):
    __tablename__ = 'vehicles'
    vin = db.Column(db.String(50), primary_key=True)
    manufacturer = db.Column(db.String(30))
    type = db.Column(db.String(30))
    inspect_date = db.Column(db.Date)
    seats = db.Column(db.Integer)
    state = db.Column(db.String(30))
