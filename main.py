from flask import Flask
from flask_restful import Api
from alembic.database import db_session, init_db

from deviceapi import DevicesAPI, DeviceAPI, DeviceStatusAPI, DeviceFirmAPI, DeviceProblemAPI, DeviceProblemsAPI    
from serviceapi import ServicesAPI, ServiceAPI, ServiceDeviceAPI
from ownerapi import OwnersAPI, OwnerAPI, OwnerDeviceAPI
from problemapi import ProblemsAPI, ProblemAPI, ProblemBranchAPI
app = Flask(__name__)
api = Api(app, prefix='/api/v1')
init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



api.add_resource(DevicesAPI, '/device')
api.add_resource(DeviceAPI, '/device/<int:deviceid>')
api.add_resource(DeviceProblemsAPI, '/device/<int:deviceid>/problem')
api.add_resource(DeviceProblemAPI, '/device/<int:deviceid>/problem/<int:problemid>')
api.add_resource(DeviceStatusAPI, '/device/findByStatus')
api.add_resource(DeviceFirmAPI, '/device/findByFirm')

api.add_resource(ServicesAPI, '/service')
api.add_resource(ServiceDeviceAPI, '/service/device')
api.add_resource(ServiceAPI, '/service/<int:serviceid>')

api.add_resource(OwnersAPI, '/user')
api.add_resource(OwnerAPI, '/user/<username>')
api.add_resource(OwnerDeviceAPI, '/user/<username>/device')

api.add_resource(ProblemsAPI, '/problem')
api.add_resource(ProblemAPI, '/problem/<int:problemid>')
api.add_resource(ProblemBranchAPI, '/problem/findByBranch')

