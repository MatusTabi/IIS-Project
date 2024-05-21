from models import Users

class AuthService:
    
    @staticmethod
    def get_user(username):
        return Users.query.filter_by(username=username).first()
