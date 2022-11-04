from flask import request
from flask_restful import Resource
from alembic.database import db_session
from alembic.models import Service_Center, Owner, Problem, Device, deviceStatus
from schemas import DeviceSchema, ProblemSchema
from marshmallow.exceptions import ValidationError 
from custom import json_error, errs

device_schema = DeviceSchema()
problem_schema = ProblemSchema()


class DevicesAPI(Resource):
    def get(self):
        devices=Device.query.all()
        return device_schema.dump(devices, many=True), 200
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
            
        device = Device.query.get(json_data['deviceid']) 
        if device:
            return errs.exists
        
        if not 'ownerid' in json_data:
            return json_error('Invalid request. No ownerid provided', 400)

        owner = Owner.query.get(json_data['ownerid'])
        if not owner:
            return json_error('Invalid request. Owner not found', 400)

        try:
            data = device_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Created device.", "device": json_data}

    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
            
        device = Device.query.get(json_data['deviceid']) 
        if not device:
            return errs.not_found
        
        owner = Owner.query.get(json_data['ownerid'])
        if not owner:
            return json_error('Invalid request. Owner not found', 400)
        try:
            data = device_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Updated device.", "device": json_data}

class DeviceStatusAPI(Resource):
    def get(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        
        status = json_data.get('status', None)

        deviceStatuses = [e.name for e in deviceStatus]
        if status not in deviceStatuses and status is not None:
            return json_error('Invalid request. Bad status value. Must be on of: ' + ', '.join(deviceStatuses) + ' or null', 400)
        
        devices=Device.query.filter_by(status=status)
        return device_schema.dump(devices, many=True), 200

class DeviceFirmAPI(Resource):
    def get(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        
        if len(json_data) != 1 or 'firm' not in json_data:
            return json_error('Only firm field must be provided', 400)
            
        firm = json_data['firm']
        
        devices=Device.query.filter_by(firm=firm)
        return device_schema.dump(devices, many=True), 200

class DeviceAPI(Resource):
    def get(self, deviceid):
        device=Device.query.get(deviceid)
        if not device:
            return errs.not_found
        return device_schema.dump(device), 200
    
    def delete(self, deviceid):
        device=Device.query.get(deviceid)
        if not device:
            return errs.not_found
        db_session.delete(device)
        db_session.commit()
        return '', 204


class DeviceProblemsAPI(Resource):
    def get(self, deviceid):
        device=Device.query.get(deviceid)
        if not device:
            return errs.not_found
        
        return {'device':device_schema.dump(device), 'problems':problem_schema.dump(device.problems, many=True)}, 200
    
    def post(self, deviceid):
        device=Device.query.get(deviceid)
        if not device:
            return errs.not_found

        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        if 'problemid' not in json_data:
            return errs.bad_request
        problem = Problem.query.get(json_data['problemid'])
        if problem:
            return errs.exists
        
        try:
            data =  problem_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        device.problems.append(data)
        db_session.add(data)
        db_session.commit()
        return {'device':device_schema.dump(device), 'Added new problem': json_data}, 200



class DeviceProblemAPI(Resource):
    def get(self, deviceid, problemid):
        device=Device.query.get(deviceid)
        if not device:
            return json_error('Device not found', 404)
        
        problem = None
        for pr in device.problems:
            if pr.problemid == problemid:
                problem = pr
        
        if not problem:
            return json_error('Problem not found', 404)
        return {'device':device_schema.dump(device),'problem':problem_schema.dump(problem)}, 200
    
    def delete(self, deviceid, problemid):
        device=Device.query.get(deviceid)
        if not device:
            return json_error('Device not found', 404)
        
        problem = None
        for pr in device.problems:
            if pr.problemid == problemid:
                problem = pr
        
        if not problem:
            return json_error('Problem not found', 404)
        db_session.delete(problem)
        db_session.commit()
        return '', 204

    def put(self, deviceid, problemid):
        device=Device.query.get(deviceid)
        if not device:
            return json_error('Device not found', 404)

        problem = Problem.query.get(problemid)
        if not problem:
            return json_error('Problem not found', 404)
        device.problems.append(problem)
        db_session.commit()
        return {'device':device_schema.dump(device),'Added existing problem':problem_schema.dump(problem)}, 200