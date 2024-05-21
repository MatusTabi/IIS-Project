from init import db

class Malfunction(db.Model):    
    __tablename__ = 'malfunction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vin = db.Column(db.String(50), db.ForeignKey('vehicles.vin'), nullable=False)
    message = db.Column(db.String(100))
    created = db.Column(db.Boolean, default=False)
    
    vin_r = db.relationship('Vehicles', backref=db.backref('malfunction', lazy=True))
    