from init import db

class Ride(db.Model):
    __tablename__ = 'ride'
    id = db.Column(db.Integer, primary_key=True)
    line_name = db.Column(db.String(10), db.ForeignKey('trafficline.line_name', ondelete='CASCADE'))
    vehicle_vin = db.Column(db.String(50), db.ForeignKey('vehicles.vin'))
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    driver = db.relationship('Users', backref='rides', lazy="joined")
    vehicle = db.relationship('Vehicles', backref='rides', lazy="joined")
