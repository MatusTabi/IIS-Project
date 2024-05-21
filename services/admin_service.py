from flask import flash, session
from sqlalchemy import exc
from sqlalchemy.orm.exc import UnmappedInstanceError

from init import db, bcrypt
from models import Users

class AdminService():
    @staticmethod
    def create_user(username, password, role):
        try:
            user = Users(username=username, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            flash('User created successfully.', 'successCU')
        except exc.IntegrityError:
            db.session.rollback()
            flash('Username already exists.', 'errorCU')
        except exc.DataError:
            db.session.rollback()
            flash('Username is too long. Maximum length is 30 characters.', 'errorCU')
        except:
            db.session.rollback()
            flash('Something went wrong.', 'errorCU')

    @staticmethod
    def delete_user(user_id):
        try:
            user = Users.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully.', 'successDU')
        except UnmappedInstanceError:
            db.session.rollback()
            flash('User does not exist.', 'errorDU')
        except:
            db.session.rollback()
            flash('Something went wrong.', 'errorDU')

    @staticmethod
    def update_user(user_id, username, password, role):
        try:
            user = Users.query.filter_by(id=user_id).first()
            user.username = username
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.role = role
            db.session.commit()
            flash('User updated successfully.', 'successUU')
        except exc.IntegrityError:
            db.session.rollback()
            flash('Username already exists.', 'errorUU')
        except exc.DataError:
            db.session.rollback()
            flash('Username is too long. Maximum length is 30 characters.', 'errorUU')
        except:
            db.session.rollback()
            flash('Something went wrong.', 'errorUU')
