from flask import flash, session
from sqlalchemy import exc, func, exists
from sqlalchemy.orm.exc import UnmappedInstanceError
from datetime import datetime

from init import db
from models import TrafficLine, Stop, TimeStop, Vehicles, Malfunction, Maintenance, Departures, Users

from typing import List

class ModeratorService():
    
    # Adding traffic line into a database.
    @staticmethod
    def create_line(traffic_line_name: str):
        trafficline = TrafficLine(line_name=traffic_line_name)
        try:
            db.session.add(trafficline)
            db.session.commit()
            flash('Traffic line created successfully.', 'successCTL')
        except exc.IntegrityError:
            flash('This traffic line already exists!', 'errorCTL')
            db.session.rollback()
        except exc.DataError:
            flash('Maximum allowed length is 10 characters', 'errorCTL')
            db.session.rollback()
    
    # Deleting traffic line from a database. If user tries to delete traffic line that
    # is currently stored in session, function will set it to empty string.
    @staticmethod
    def delete_line(traffic_line_name: str):
        traffic_line_to_delete = TrafficLine.query.filter_by(line_name=traffic_line_name).first()
        try:
            ModeratorService.__reset_select(traffic_line_to_delete)
            db.session.delete(traffic_line_to_delete)
            db.session.commit()
            flash('Traffic line deleted successfully.', 'successDTL')
        except UnmappedInstanceError:
            flash('This traffic line does not exist!', 'errorDTL')
            db.session.rollback()
            
    # Reseting session['selected_line'] when moderator deletes a traffic line that
    # is currently stored in a session.
    @staticmethod
    def __reset_select(traffic_line: TrafficLine):
        if 'selected_line' in session and session['selected_line'] == traffic_line.line_name:
            session['selected_line'] = ''
    
    # Adding new stop into a database.
    @staticmethod
    def create_stop(stop_name: str):
        stop = Stop(name=stop_name)
        try:
            db.session.add(stop)
            db.session.commit()
            flash('Stop created successfully.', 'successCS')
        except exc.IntegrityError:
            flash('This stop already exists!', 'errorCS')
            db.session.rollback()
        except exc.DataError:
            flash('Maximum allowed length is 50 characters!', 'errorCS')
            db.session.rollback()
    
    # Deleting stop from a database. Function will adjust the order of stops in all lines that 
    # have this stop which will be deleted. If the stop was the last stop within traffic line,
    # first and last stop will be reseted.
    @staticmethod
    def delete_stop(stop_name: str):
        stop_to_delete = Stop.query.filter_by(name=stop_name).first()
        print(stop_to_delete.name)
        try:
            lines = ModeratorService.__adjust_order(stop_name)
            db.session.delete(stop_to_delete)
            for line in lines:
                ModeratorService.__reset_first_last_line(line.line_name)
                ModeratorService.__update_line(line.line_name)
            db.session.commit()
            flash('Stop deleted successfully.', 'successDS')
        except UnmappedInstanceError:
            flash('This stop does not exist!', 'errorDS')
            db.session.rollback()   
    
    # Adjusting the order of stops in each line that has the deleting stop.
    # 
    # For each line filtered by a deleting stop, deleting stops ID is selected. Since stops
    # in traffic line are order by a from starting stop index, each from starting stop index above
    # the deleting stop will be decremented. Potentially, the traffic line can have multiple identical
    # stops, and therefore from start indexes must be appropiately adjusted in for cycle.
    @staticmethod
    def __adjust_order(deleted_stop: str) -> List[TrafficLine]:
        lines = TimeStop.query.filter_by(stop_name=deleted_stop).distinct(TimeStop.line_name).all()
        for line in lines:
            stops = db.session.query(TimeStop.id).filter_by(line_name=line.line_name).\
                        filter_by(stop_name=deleted_stop).all()
            for stop in stops:
                deletion = TimeStop.query.filter_by(id=stop.id).first()
                update = TimeStop.query.filter_by(line_name=line.line_name).\
                    order_by(TimeStop.from_start.asc()).\
                    offset(deletion.from_start + 1).all()
                if not update == []:
                    for row in update:
                        row.from_start -= 1
        return lines    
    
    # If the deleting stop was the last stop in traffic line, starting and last stop
    # are set to None.
    @staticmethod    
    def __reset_first_last_line(selected_line: str):
        if TimeStop.query.filter_by(line_name=selected_line).first() == None:
            update = TrafficLine.query.filter_by(line_name=selected_line).first()
            update.starting_stop = None
            update.last_stop = None

    # Adding stop into a traffic line.
    # 
    # Function checks if moderator entered correct from starting stop index.
    # If moderator tried to insert stop between already existing stops, from starting stop
    # indexes will be adjusted.
    @staticmethod
    def add_stop_to_line(from_start: int, new_name: str):
        try:
            if TimeStop.query.filter_by(line_name=session['selected_line']).all() == [] and from_start != 0:
                flash('First stop index must be 0!', 'errorAS')
                return
            time_stop = TimeStop(is_start=False, is_end=False, from_start=from_start,
                                line_name=session['selected_line'], stop_name=new_name)
            update = TimeStop.query.filter_by(line_name=time_stop.line_name).\
                        order_by(TimeStop.from_start.asc()).\
                        offset(time_stop.from_start).all()

            last_stop = TimeStop.query.filter_by(line_name=time_stop.line_name).\
                        order_by(TimeStop.from_start.desc()).first()
            if not last_stop == None and last_stop.from_start + 1 < from_start:
                raise exc.SQLAlchemyError
            if not update == []:
                for row in update:
                    row.from_start += 1
            db.session.add(time_stop)
            ModeratorService.__update_line(session['selected_line'])
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            flash('Wrong stop index, try again!', 'errorAS')
        except KeyError:
            flash('You did not select traffic line!', 'errorAS')
    
    # Setting starting and last stop.
    @staticmethod        
    def __update_line(selected_line: str):
        line = TrafficLine.query.filter_by(line_name=selected_line).first()
        first_stop = TimeStop.query.filter_by(line_name=selected_line).\
                        order_by(TimeStop.from_start.asc()).first()
        last_stop = TimeStop.query.filter_by(line_name=selected_line).\
                        order_by(TimeStop.from_start.desc()).first()
        line.starting_stop = first_stop.stop.name
        line.last_stop = last_stop.stop.name
        
    # Deleting stops from traffic line.
    # 
    # Function is updating and reseting starting and last line within traffic line.
    @staticmethod
    def delete_stop_from_tl(id: int):
        deletion = TimeStop.query.filter_by(id=id).first()
        update = TimeStop.query.filter_by(line_name=deletion.line_name).\
                    order_by(TimeStop.from_start.asc()).\
                    offset(deletion.from_start + 1).all()
        if not update == []:
            for row in update:
                row.from_start -= 1
        try:
            if not TimeStop.query.filter_by(line_name=deletion.line_name).first() == None:
                ModeratorService.__update_line(session['selected_line'])
            db.session.delete(deletion)
            ModeratorService.__reset_first_last_line(session['selected_line'])
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
    
    # Adding new vehicle into a database.
    @staticmethod
    def add_vehicle(vin, manufacturer, v_type, seats, state):
        try:    
            new_vehicle = Vehicles(vin=vin, manufacturer=manufacturer, type=v_type, inspect_date=None,
                                seats=seats, state=state)
            db.session.add(new_vehicle)
            db.session.commit()
        except exc.DataError:
            flash('You entered wrong input, try again!', 'errorV')
        except exc.SQLAlchemyError:
            db.session.rollback()
            
    # Deleting vehicle from a database.
    @staticmethod
    def delete_vehicle(vin):
        deletion = Vehicles.query.filter_by(vin=vin).first()
        try:
            db.session.delete(deletion)
            db.session.commit()
        except:
            db.session.rollback()
            
    # Creating request for engineer.
    # 
    # For each malfunction driver created for a vehicle, moderator creates maintenance request
    # for engineers. Maintenance request is set to a engineer, that has the lowest number of 
    # maintenance requests.
    @staticmethod
    def create_request(id, user_id):
        malfunction = Malfunction.query.filter_by(id=id).first()
        malfunction.created = True
        engineer = db.session.query(Maintenance.engineer).\
            group_by(Maintenance.engineer).\
            order_by(func.count(Maintenance.engineer)).first()
        unused = db.session.query(Users).filter_by(role="engineer").\
                filter(~exists().where(Users.id == Maintenance.engineer)).first()
        if unused != None:
            engineer_id = unused.id
        elif engineer == None:
            engineer = db.session.query(Users).filter_by(role="engineer").first()
            engineer_id = engineer.id
        else:
            engineer_id = engineer[0]
            
        try:
            new_request = Maintenance(ticketID=id, vin=malfunction.vin, engineer=engineer_id, moderator=user_id, 
                            date=datetime.today().strftime('%Y-%m-%d'), request=malfunction.message, 
                            report=None, state=None)
            db.session.add(new_request)
            db.session.commit()
        except exc.IntegrityError:
            flash('Request was already created!', 'errorV')
        except exc.SQLAlchemyError:
            db.session.rollback()
    
    # Editing manufacturer field for a vehicle.
    @staticmethod
    def edit_manufacturer(vin, manufacrurer):
        vehicle = Vehicles.query.filter_by(vin=vin).first()
        vehicle.manufacturer = manufacrurer
        try:
            db.session.commit()
        except:
            db.session.rollback()
            
    # Editing type field for a vehicle.
    @staticmethod
    def edit_type(vin, type):
        vehicle = Vehicles.query.filter_by(vin=vin).first()
        vehicle.type = type
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    # Editing seats field for a vehicle.
    @staticmethod
    def edit_seats(vin, seats):
        vehicle = Vehicles.query.filter_by(vin=vin).first()
        vehicle.seats = seats
        try:
            db.session.commit()
        except:
            db.session.rollback() 

    # Adding departure times to a stop within a traffic line.
    @staticmethod
    def add_departures(stop_name, line_name, direction, stop_name_list, times):
        max_order = db.session.query(func.max(Departures.order_number)).filter_by(line_name=line_name).scalar() or 0
        max_order += 1
        try:
            for index, stop in enumerate(stop_name_list):
                time = times[index][f'time_{stop}']
                new_times = Departures(line_name=line_name, stop_name=stop, time=datetime.strptime(time, '%H:%M').time(), 
                                    order_number=max_order, direction=direction)
                db.session.add(new_times)
            db.session.commit()
        except Exception as e:
            flash('Wrong departure time input at traffic line ' f'{line_name}!', 'errorDEP')
            db.session.rollback()
            