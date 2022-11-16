from flask import request
from flask_restful import Resource
from alembic.database import db_session
from alembic.models import Service_Center, Owner, Problem, Device, deviceStatus
from schemas import ServiceCenterSchema
from marshmallow.exceptions import ValidationError 
from custom import json_error, errs

service_schema = ServiceCenterSchema()


class ServicesAPI(Resource):
    def get(self):
        services=Service_Center.query.all()
        return service_schema.dump(services, many=True), 200
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
            
        service = Service_Center.query.get(json_data['serviceid']) 
        if service:
            return errs.exists
        
        
        try:
            data = service_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Created service.", "service": json_data}

    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
            
        service = Service_Center.query.get(json_data['serviceid']) 
        if not service:
            return errs.not_found
        
        try:
            data = service_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Updated service.", "service": json_data}

class ServiceAPI(Resource):
    def get(self, serviceid):
        service=Service_Center.query.get(serviceid)
        if not service:
            return errs.not_found
        return service_schema.dump(service), 200
    
    def delete(self, serviceid):
        service=Service_Center.query.get(serviceid)
        if not service:
            return errs.not_found
        db_session.delete(service)
        db_session.commit()
        return '', 204



class ServiceDeviceAPI(Resource):
    def get(self):
        statuses = [e.name for e in deviceStatus] + [None]
        result = {}
        
        for status in statuses:
            result[status] = len(Device.query.filter_by(status=status).all())
        return result, 200
    

