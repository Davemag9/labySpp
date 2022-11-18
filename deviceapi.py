from flask import request
from flask_restful import Resource
from alembic.database import db_session
from alembic.models import Service_Center, User, Problem, Device, deviceStatus
from schemas import DeviceSchema, ProblemSchema
from marshmallow.exceptions import ValidationError
from custom import json_error, errs
from main import bcrypt, master_required, admin_required, get_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token

device_schema = DeviceSchema()
problem_schema = ProblemSchema()


class DevicesAPI(Resource):
    @admin_required()
    def get(self):
        devices = Device.query.all()
        return device_schema.dump(devices, many=True), 200

    @master_required()
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request

        device = Device.query.get(json_data.get('deviceid', None))
        if device:
            return errs.exists

        if not 'userid' in json_data:
            return json_error('Invalid request. No userid provided', 400)

        user = User.query.get(json_data.get('userid', None))
        if not user:
            return json_error('Invalid request. User not found', 400)
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != user.service_centerid:
            return json_error("Forbidden. Master can add devices only of his clients.", 403)
        try:
            data = device_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Created device.", "device": json_data}

    @master_required()
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request

        device = Device.query.get(json_data.get('deviceid', None))
        if not device:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. Master can change devices only of his clients.", 403)

        user = User.query.get(json_data.get('userid', None))
        if not user:
            return json_error('Invalid request. User not found', 400)

        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != user.service_centerid:
            return json_error("Forbidden. Master can assign devices only to his clients.", 403)
        try:
            data = device_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Updated device.", "device": json_data}


class DeviceStatusAPI(Resource):
    @admin_required()
    def get(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request

        status = json_data.get('status', None)

        deviceStatuses = [e.name for e in deviceStatus]
        if status not in deviceStatuses and status is not None:
            return json_error(
                'Invalid request. Bad status value. Must be on of: ' + ', '.join(deviceStatuses) + ' or null', 400)

        devices = Device.query.filter_by(status=status)
        return device_schema.dump(devices, many=True), 200


class DeviceFirmAPI(Resource):
    @admin_required()
    def get(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request

        if len(json_data) != 1 or 'firm' not in json_data:
            return json_error('Only firm field must be provided', 400)

        firm = json_data['firm']

        devices = Device.query.filter_by(firm=firm)
        return device_schema.dump(devices, many=True), 200


class DeviceAPI(Resource):
    @jwt_required()
    def get(self, deviceid):
        device = Device.query.get(deviceid)
        if not device:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. User can get info about his devices.", 403)
        return device_schema.dump(device), 200

    @master_required()
    def delete(self, deviceid):
        device = Device.query.get(deviceid)
        if not device:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. Master can delete devices only from his clients.", 403)
        db_session.delete(device)
        db_session.commit()
        return '', 204


class DeviceProblemsAPI(Resource):
    @jwt_required()
    def get(self, deviceid):
        device = Device.query.get(deviceid)
        if not device:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. User can get info about problems only of his devices.", 403)
        return {'device': device_schema.dump(device), 'problems': problem_schema.dump(device.problems, many=True)}, 200

    @master_required()
    def post(self, deviceid):
        device = Device.query.get(deviceid)
        if not device:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. Master can add problems only to his client's devices.", 403)
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        if 'problemid' not in json_data:
            return errs.bad_request
        problem = Problem.query.get(json_data.get('problemid', None))
        if problem:
            return errs.exists

        try:
            data = problem_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        device.problems.append(data)
        db_session.add(data)
        db_session.commit()
        return {'device': device_schema.dump(device), 'Added new problem': json_data}, 200


class DeviceProblemAPI(Resource):
    @jwt_required()
    def get(self, deviceid, problemid):
        device = Device.query.get(deviceid)
        if not device:
            return json_error('Device not found', 404)
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. User can get info only about his problems.", 403)
        problem = None
        for pr in device.problems:
            if pr.problemid == problemid:
                problem = pr

        if not problem:
            return json_error('Problem not found', 404)
        return {'device': device_schema.dump(device), 'problem': problem_schema.dump(problem)}, 200

    @master_required()
    def delete(self, deviceid, problemid):
        device = Device.query.get(deviceid)
        if not device:
            return json_error('Device not found', 404)
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. Only master can delete only problems of his devices.", 403)
        problem = None
        for pr in device.problems:
            if pr.problemid == problemid:
                problem = pr

        if not problem:
            return json_error('Problem not found', 404)
        db_session.delete(problem)
        db_session.commit()
        return '', 204

    @master_required()
    def put(self, deviceid, problemid):
        device = Device.query.get(deviceid)
        if not device:
            return json_error('Device not found', 404)
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != device.user.service_centerid:
            return json_error("Forbidden. Only master can update only problems of his devices.", 403)
        problem = Problem.query.get(problemid)
        if not problem:
            return json_error('Problem not found', 404)
        device.problems.append(problem)
        db_session.commit()
        return {'device': device_schema.dump(device), 'Added existing problem': problem_schema.dump(problem)}, 200
