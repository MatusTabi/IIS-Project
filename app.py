from flask import render_template, request, redirect, flash, url_for, session
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import or_, and_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy import exc, func, Time
from datetime import datetime, date, time, timedelta, timezone
from sqlalchemy import extract

from init import app, db, bcrypt, login_manager
from models import Users, Stop, TrafficLine, Departures, Maintenance, Malfunction, Ride, TimeStop, Vehicles
from controllers import admin, moderator, dispatcher, auth, engineer, driver

INACTIVITY_PERIOD = timedelta(minutes=10)

#print(bcrypt.generate_password_hash('admin_100').decode('utf-8'))
#print(bcrypt.generate_password_hash('moderator_120').decode('utf-8'))
#print(bcrypt.generate_password_hash('engineer_420').decode('utf-8'))
#print(bcrypt.generate_password_hash('dispatcher_111').decode('utf-8'))
#print(bcrypt.generate_password_hash('driver_222').decode('utf-8'))

app.register_blueprint(admin)
app.register_blueprint(moderator)
app.register_blueprint(dispatcher)
app.register_blueprint(auth)
app.register_blueprint(engineer)
app.register_blueprint(driver)

@app.before_request
def check_inactivity():
    if current_user.is_authenticated:
        last_activity = session['last_activity'] if 'last_activity' in session else None
        session['last_activity'] = datetime.now(timezone.utc)
        if last_activity and datetime.now(timezone.utc) - last_activity > INACTIVITY_PERIOD:
            logout_user()
            flash('You were logged out due to inactivity.')
            return redirect(url_for('auth.login'))

@app.route('/home')
@app.route('/', methods=['GET'])
def index():
    lines = TrafficLine.query.all()
    return render_template('index.html', lines=lines)

@app.route('/search', methods=['GET'])
def search():
    selected_line = request.args.get('line', '')
    line = TrafficLine.query.filter_by(line_name=selected_line).first()
    stops_in_line = TimeStop.query.filter_by(line_name=selected_line).order_by(TimeStop.from_start).all()
    deps_of_line = Departures.query.filter_by(line_name=selected_line).order_by(Departures.time).all()
    line_true_dir = {}
    line_false_dir = {}
    for i in reversed(stops_in_line):
        lst_2d = {}
        for j in range(0,24):
            lst_1d = []
            #najst kolko deps je v danej hodine na danej zastafke
            deps_true = Departures.query.filter_by(line_name=selected_line).\
                    filter_by(stop_name=i.stop_name).\
                    filter_by(direction=True).\
                    filter(extract('hour', Departures.time) == j).all()
            for k in deps_true:
                t = k.time
                lst_1d.append(t.strftime('%M'))
            lst_1d = list(dict.fromkeys(lst_1d))
            lst_1d.sort()
            index = '{:0>2}'.format(j)
            lst_2d[index] = lst_1d
        line_true_dir[i.stop_name] = lst_2d
    for i in stops_in_line:
        lst_2d = {}
        for j in range(0,24):
            lst_1d = []
            #najst kolko deps je v danej hodine na danej zastafke
            deps_false = Departures.query.filter_by(line_name=selected_line).\
                    filter_by(stop_name=i.stop_name).\
                    filter_by(direction=False).\
                    filter(extract('hour', Departures.time) == j).all()
            for k in deps_false:
                t = k.time
                lst_1d.append(t.strftime('%M'))
            lst_1d = list(dict.fromkeys(lst_1d))
            lst_1d.sort()
            index = '{:0>2}'.format(j)
            lst_2d[index] = lst_1d
        line_false_dir[i.stop_name] = lst_2d
    
    #change poradie depst

    return render_template('search_lines.html', depst=line_true_dir, depsf=line_false_dir, line=line)

def get_admin_args():
    args = {
        'users': Users.query.all(),
        'show_modal': False,
        'selected_user': None
    }

    action = request.form.get('action')

    if action == 'show-modal':
        args['show_modal'] = True
        args['selected_user'] = Users.query.filter_by(id=request.form.get('user_id')).first()
    elif action == 'close-modal':
        args['show_modal'] = False
        args['selected_user'] = None

    return args

def get_moderator_args():
    args =  {
        'traffic_lines': None,
        'stops': Stop.query.all(),
        'vehicles': Vehicles.query.all(),
        'timestop': None,
        'selected_line': '',
        'stops_in_tl': []
    }
    
    traffic_lines = TrafficLine.query.all()
    args['traffic_lines'] = traffic_lines
    for traffic_line in traffic_lines:
        stops = TimeStop.query.filter_by(line_name=traffic_line.line_name).order_by(TimeStop.from_start).all()
        # stops = [stop.stop_name for stop in traffic_line.stops]
        args['stops_in_tl'].append({'line': traffic_line, 'stops':stops})
    
    if request.args.get('name') is not None:
        session['selected_line'] = request.args.get('name')
    if 'selected_line' in session:
        args['selected_line'] = session['selected_line']
        args['timestop'] = db.session.query(Stop.name, TimeStop.from_start, TimeStop.id).\
            join(TimeStop, Stop.name == TimeStop.stop_name).\
            join(TrafficLine, TimeStop.line_name == TrafficLine.line_name).\
            filter(TrafficLine.line_name == session['selected_line']).\
            order_by(TimeStop.from_start.asc()).all()
    else:
        flash('Please select a line to display stops.', 'infoS')
    
    return args

def get_engineer_args():
    if current_user.role == 'admin':
        modelQuery = Maintenance.query.order_by(Maintenance.ticketID).all()
    else:
        modelQuery = Maintenance.query.filter_by(engineer=current_user.id).order_by(Maintenance.ticketID)
    moderators = Users.query.filter_by(role="moderator")
    return {
        'maintenance': modelQuery,
        'mods' : moderators
    }

def get_driver_args():
    if current_user.role == 'admin':
        ridesQuery = Ride.query.order_by(Ride.id).all()
    else:
        ridesQuery = Ride.query.filter_by(driver_id=current_user.id).order_by(Ride.id)
    vehicles = Vehicles.query.all()
    return {
        'rides': ridesQuery,
        'vehicles' : vehicles
    }

def get_dispatcher_args():
    traffic_lines = TrafficLine.query.all()
    traffic_line_stops = {}

    for tl in traffic_lines:
        stop_count = TimeStop.query.filter_by(line_name=tl.line_name).count()
        traffic_line_stops[tl.line_name] = stop_count

    selected_tl_name = session.get('selected_tl')
    tl_rides = Ride.query.filter_by(line_name=selected_tl_name).order_by(Ride.start_time).all() if selected_tl_name else []

    args = {
        'traffic_lines': traffic_lines,
        'traffic_line_stops': traffic_line_stops,
        'selected_tl': selected_tl_name,
        'tl_rides': tl_rides,
        'show_modal': False,
        'start_time': None,
        'end_time': None,
        'available_vehicles': [],
        'available_drivers': []
    }

    action = request.form.get('action')

    if action == 'select-tl':
        selected_tl_name = request.form.get('tl_name')
        if selected_tl_name:
            session['selected_tl'] = selected_tl_name
            args['selected_tl'] = selected_tl_name
            args['tl_rides'] = Ride.query.filter_by(line_name=selected_tl_name).all()

    elif action == 'show-modal':
        args['show_modal'] = True

    elif action == 'close-modal':
        args['show_modal'] = False

    elif action == 'check-availability':
        args['show_modal'] = True
        args['start_time'] = request.form.get('start_time')
        args['end_time'] = request.form.get('end_time')
        args['available_vehicles'], args['available_drivers'] = handle_availability_check(request)

    return args


def handle_availability_check(request):
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    if start_time and end_time:
        start_time = datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.strptime(end_time, '%H:%M').time()

        available_drivers = db.session.query(Users) \
            .filter(Users.role == 'driver') \
            .filter(
                not_(
                    db.session.query(Ride) \
                    .filter(Ride.driver_id == Users.id) \
                    .filter(Ride.start_time < end_time) \
                    .filter(Ride.end_time > start_time) \
                    .exists()
                )
            ).all()

        available_vehicles = db.session.query(Vehicles) \
            .filter(
                not_(
                    db.session.query(Ride) \
                    .filter(Ride.vehicle_vin == Vehicles.vin) \
                    .filter(Ride.start_time < end_time) \
                    .filter(Ride.end_time > start_time) \
                    .exists()
                )
            ).all()

        return available_vehicles, available_drivers
    else:
        return [], []

role_template = {
    'admin': {
        'template': 'admin.html',
        'args': 'get_admin_args'
    },
    
    'moderator': {
        'template': 'moderator.html',
        'args': 'get_moderator_args'
    },
    
    'engineer': {
        'template': 'engineer.html',
        'args': 'get_engineer_args'
    },
    
    'dispatcher': {
        'template': 'dispatcher.html',
        'args': 'get_dispatcher_args'
    },
    
    'driver': {
        'template': 'driver.html',
        'args': 'get_driver_args'
    }
}


@app.route('/system', methods=['POST', 'GET'])
@login_required
def system():
    user_role = session.get('become_role', current_user.role)

    if request.method == 'POST':
        if current_user.role == 'admin':
            action = request.form.get('action')
            if action == 'become-user':
                become_role = request.form.get('user_role')
                if become_role in role_template and become_role != 'admin':
                    session['become_role'] = become_role
                    user_role = become_role
                else:
                    flash('Invalid role or already an admin', 'errorBU')

    if current_user.is_authenticated:
        template_info = role_template.get(user_role)
        if template_info:
            template = template_info['template']
            function_name = template_info['args']
            args = globals()[function_name]() if function_name in globals() and callable(globals()[function_name]) else {}
            return render_template(template, **args)
        else:
            return render_template('error.html')
    else:
        return 'User not logged in'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
