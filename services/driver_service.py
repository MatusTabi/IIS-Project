from flask import flash, session
from sqlalchemy import exc, func
from sqlalchemy.orm.exc import UnmappedInstanceError
from datetime import datetime

from init import db
from models import TrafficLine, Stop, TimeStop, Vehicles, Malfunction, Maintenance, Departures

from typing import List

class DriverService():
      @staticmethod
      def send_message(report,vehicle):
        new_message = Malfunction(vin=vehicle,message=report)
        try:
            db.session.add(new_message)
            db.session.commit()
            flash('Message sent successfully.', 'successSRM')
        except BaseException as error:
            flash('Could not send message!' + report + vehicle, 'errorSRM')
            db.session.rollback()