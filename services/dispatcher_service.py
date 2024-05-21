from flask import flash, session
from sqlalchemy import exc
from sqlalchemy.orm.exc import UnmappedInstanceError
from datetime import datetime

from init import db
from models import Ride

class DispatcherService():
    @staticmethod
    def add_ride(line_name, vehicle_vin, driver_id, start_time, end_time):
        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            ride = Ride(line_name=line_name, vehicle_vin=vehicle_vin, driver_id=driver_id, start_time=start_time_obj, end_time=end_time_obj)
            db.session.add(ride)
            db.session.commit()
            flash('Ride added successfully.', 'successAR')
        except exc.IntegrityError:
            db.session.rollback()
            flash('Ride already exists.', 'errorAR')
        except:
            db.session.rollback()
            flash('Something went wrong.', 'errorAR')

    @staticmethod
    def remove_ride(ride_id):
        try:
            ride = Ride.query.filter_by(id=ride_id).first()
            db.session.delete(ride)
            db.session.commit()
            flash('Ride deleted successfully.', 'successRR')
        except UnmappedInstanceError:
            db.session.rollback()
            flash('Ride does not exist.', 'errorRR')
        except:
            db.session.rollback()
            flash('Something went wrong.', 'errorRR')
