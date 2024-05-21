from flask import redirect, url_for, request, session, flash, render_template, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta

from init import login_manager, db, bcrypt
from models import Users 
from services import AuthService

auth = Blueprint('auth', __name__)

@login_manager.unauthorized_handler
def unauthorized():
    flash('You don\'t have access to this page. Please log in.')
    return redirect(url_for('login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('system'))

    if request.method == 'POST':
        username = request.form['username']
        user = AuthService.get_user(username)
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('system'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    if session.get('become_role'):
        session.pop('become_role', None)
        return redirect(url_for('system'))
    else:
        logout_user()
        return redirect(url_for('auth.login'))

@login_manager.user_loader
def loaderUser(id):
    return db.session.get(Users, id)
