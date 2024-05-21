from flask import flash, session
from sqlalchemy import exc, func
from sqlalchemy.orm.exc import UnmappedInstanceError
from datetime import datetime

from init import db
from models import TrafficLine, Stop, TimeStop, Vehicles, Malfunction, Maintenance, Departures

from typing import List

class EngineerService():
    @staticmethod
    def update_ticket(ticket_update,report,state):
        if ticket_update != None:
            column = Maintenance.query.get(ticket_update)
            try:
                if state == "done":
                    try :
                        done = Malfunction.query.filter(Malfunction.id==ticket_update).first()
                        db.session.delete(done)
                        db.session.commit()
                    except BaseException as error:
                        db.session.rollback()
                column.report = report
                column.state = state
                db.session.commit()
                flash('Message updated successfully.', 'successUEM')
            except BaseException as error:
                flash('Could not update message!', 'errorUEM')
                db.session.rollback()