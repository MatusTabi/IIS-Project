from flask import request, redirect, url_for, Blueprint
from flask_login import current_user

from services import DispatcherService

dispatcher = Blueprint('dispatcher', __name__)

@dispatcher.route('/add_ride', methods=['POST'])
def add_ride():
    if request.form['action'] == 'add-ride':
        line_name = request.form['line_name']
        vehicle_vin = request.form['vehicle_vin']
        driver_id = request.form['driver_id']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        DispatcherService.add_ride(line_name, vehicle_vin, driver_id, start_time, end_time)
    return redirect(url_for('system'))

@dispatcher.route('/remove_ride', methods=['POST'])
def remove_ride():
    if request.form['action'] == 'remove-ride':
        ride_id = request.form['ride_id']

        DispatcherService.remove_ride(ride_id)
    return redirect(url_for('system'))
