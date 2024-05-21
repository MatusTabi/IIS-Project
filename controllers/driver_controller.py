from flask import request, redirect, url_for, flash, Blueprint
from flask_login import current_user

from services import DriverService

driver = Blueprint('driver',__name__)

@driver.route('/send_message', methods=['POST','GET'])
def send_message():
    if request.method == 'POST':
        report = request.form.get('report')
        vehicle = request.form.get('vehicle')
        DriverService.send_message(report,vehicle)
    return redirect(url_for('system'))




