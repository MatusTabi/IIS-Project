from init import db

class TimeStop(db.Model):
    __tablename__ = 'timestop'
    id = db.Column(db.Integer, primary_key=True)
    is_start = db.Column(db.Boolean, default=False)
    is_end = db.Column(db.Boolean, default=False)
    from_start = db.Column(db.Integer, default=0)
    
    line_name = db.Column(db.String(10), db.ForeignKey('trafficline.line_name'), nullable=False)
    stop_name = db.Column(db.String(50), db.ForeignKey('stop.name'), nullable=False)
    
    trafficLine = db.relationship('TrafficLine', backref=db.backref('timestop', lazy=True,
                                                                    cascade='all, delete-orphan'), foreign_keys=[line_name])
    stop = db.relationship('Stop', backref=db.backref('timestop', lazy=True,
                                                      cascade='all, delete-orphan'), foreign_keys=[stop_name])
