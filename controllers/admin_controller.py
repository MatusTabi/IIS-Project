from flask import request, redirect, url_for, Blueprint
from flask_login import current_user

from services import AdminService

admin = Blueprint('admin', __name__)

@admin.route('/create_user', methods=['POST'])
def create_user():
    if request.form['action'] == 'create-user':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        AdminService.create_user(username, password, role)
    return redirect(url_for('system'))

@admin.route('/delete_user', methods=['POST'])
def delete_user():
    if request.form['action'] == 'delete-user':
        user_id = request.form['user_id']

        AdminService.delete_user(user_id)
    return redirect(url_for('system'))

@admin.route('/update_user', methods=['POST'])
def update_user():
    if request.form['action'] == 'update-user':
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        AdminService.update_user(user_id, username, password, role)
    return redirect(url_for('system'))
