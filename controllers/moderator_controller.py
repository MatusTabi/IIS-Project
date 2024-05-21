from flask import request, redirect, url_for, flash, Blueprint
from flask_login import current_user

from services import ModeratorService

moderator = Blueprint('moderator', __name__)

@moderator.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        if request.form['action'] == 'create-line':
            traffic_line_name = request.form.get('line_name')
            ModeratorService.create_line(traffic_line_name)
        elif request.form['action'] == 'delete-line':
            traffic_line_name = request.form.get('line_name')
            ModeratorService.delete_line(traffic_line_name)
        elif request.form['action'] == 'create-stop':
            stop_name = request.form.get('name')
            ModeratorService.create_stop(stop_name)
        elif request.form['action'] == 'delete-stop':
            stop_name = request.form.get('name')
            ModeratorService.delete_stop(stop_name)
    return redirect(url_for('system'))

@moderator.route('/add_stop_to_tl', methods=['POST', 'GET'])
def add_stop_to_tl():
    if request.method == 'POST':
        new_name = request.form.get('new_name')
        try:
            from_start = int(request.form.get('from_start')) 
        except ValueError:
            flash('Stop index must be a number!', 'errorAS')
        ModeratorService.add_stop_to_line(from_start, new_name)
    return redirect(url_for('system'))

@moderator.route('/delete_stop_from_tl', methods=['POST', 'GET'])
def delete_stop_from_tl():
    if request.method == 'POST':
        id = request.form.get('action')
        ModeratorService.delete_stop_from_tl(id)
    return redirect(url_for('system'))

@moderator.route('/add_vehicle', methods=['POST', 'GET'])
def add_vehicle():
    if request.method == 'POST':
        vin = request.form.get('vin')
        manufacturer = request.form.get('manufacturer')
        v_type = request.form.get('type')
        seats = request.form.get('seats')
        state = request.form.get('state')
        ModeratorService.add_vehicle(vin, manufacturer, v_type, seats, state)
    return redirect(url_for('system'))

@moderator.route('/delete_vehicle', methods=['POST', 'GET'])
def delete_vehicle():
    if request.method == 'POST':
        vin = request.form.get('action')
        ModeratorService.delete_vehicle(vin)
    return redirect(url_for('system'))

@moderator.route('/create_request', methods=['POST', 'GET'])
def create_request():
    if request.method == 'POST':
        id = request.form.get('action')
        ModeratorService.create_request(id, current_user.id)
    return redirect(url_for('system'))    

@moderator.route('/edit_manufacturer', methods=['POST', 'GET'])
def edit_manufacturer():
    if request.method == 'POST':
        vin = request.form.get('action')
        manufacturer = request.form.get('vehicle_manufacturer')
        ModeratorService.edit_manufacturer(vin, manufacturer)    
    return redirect(url_for('system'))

@moderator.route('/edit_type', methods=['POST', 'GET'])
def edit_type():
    if request.method == 'POST':
        vin = request.form.get('action')
        type = request.form.get('vehicle_type')
        ModeratorService.edit_type(vin, type)
    return redirect(url_for('system'))

@moderator.route('/edit_seats', methods=['POST', 'GET'])
def edit_seats():
    if request.method == 'POST':
        vin = request.form.get('action')
        seats = request.form.get('vehicle_seats')
        ModeratorService.edit_seats(vin, seats)
    return redirect(url_for('system'))

@moderator.route('/add_departures', methods=['POST', 'GET'])
def add_departures():
    if request.method == 'POST':
        stop_name = request.form.get('stop_name')
        line_name = request.form.get('action')
        direction = True if request.form.get('direction') else False
        stop_name_list = request.form.getlist('stop_name')
        times = []
        for stop in stop_name_list:
            time = request.form.get(f'time_{stop}')
            times.append({f'time_{stop}': time})
        ModeratorService.add_departures(stop_name, line_name, direction, stop_name_list, times)
    return redirect(url_for('system'))
