from flask import request, redirect, url_for, flash, Blueprint
from flask_login import current_user

from services import EngineerService

engineer = Blueprint('engineer',__name__)

@engineer.route('/update_ticket', methods=['POST','GET'])
def update_ticket():
    if request.method == 'POST':
        ticket_update = request.form.get('save')
        report = request.form.get('report')
        state = request.form.get('state')
        EngineerService.update_ticket(ticket_update,report,state)
    return redirect(url_for('system'))

