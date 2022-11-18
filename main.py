from flask import Flask
from flask import jsonify
from flask_restful import Api
from alembic.database import db_session, init_db
from flask_bcrypt import Bcrypt
from custom import json_error

app = Flask(__name__)
api = Api(app, prefix='/api/v1')
bcrypt = Bcrypt(app)

init_db()

from flask_jwt_extended import get_jwt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request


app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

from functools import wraps
from alembic.models import User

def get_user():
    return User.query.filter_by(username=get_jwt()['sub'])[0]

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user = User.query.filter_by(username=claims['sub'])[0]
            if not user:
                return json_error("Authentication failed. User not found", 404)

            if user.role == 'admin':
                return fn(*args, **kwargs)
            return json_error("Must be an admin", 403)

        return decorator

    return wrapper


def master_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user = User.query.filter_by(username=claims['sub'])[0]
            if not user:
                return json_error("Authentication failed. User not found.", 404)

            if user.role == 'master' or user.role == 'admin':
                return fn(*args, **kwargs)
            return json_error("Must be a master.", 403)

        return decorator

    return wrapper


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


from deviceapi import DevicesAPI, DeviceAPI, DeviceStatusAPI, DeviceFirmAPI, DeviceProblemAPI, DeviceProblemsAPI
from serviceapi import ServicesAPI, ServiceAPI, ServiceDeviceAPI
from userapi import UsersAPI, UserAPI, UserDeviceAPI, UserLoginAPI
from problemapi import ProblemsAPI, ProblemAPI, ProblemBranchAPI

api.add_resource(DevicesAPI, '/device')
api.add_resource(DeviceAPI, '/device/<int:deviceid>')
api.add_resource(DeviceProblemsAPI, '/device/<int:deviceid>/problem')
api.add_resource(DeviceProblemAPI, '/device/<int:deviceid>/problem/<int:problemid>')
api.add_resource(DeviceStatusAPI, '/device/findByStatus')
api.add_resource(DeviceFirmAPI, '/device/findByFirm')

api.add_resource(ServicesAPI, '/service')
api.add_resource(ServiceDeviceAPI, '/service/device')
api.add_resource(ServiceAPI, '/service/<int:serviceid>')

api.add_resource(UsersAPI, '/user')
api.add_resource(UserAPI, '/user/<username>')
api.add_resource(UserDeviceAPI, '/user/<username>/device')
api.add_resource(UserLoginAPI, '/login')

api.add_resource(ProblemsAPI, '/problem')
api.add_resource(ProblemAPI, '/problem/<int:problemid>')
api.add_resource(ProblemBranchAPI, '/problem/findByBranch')
