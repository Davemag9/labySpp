from flask import request
from flask_restful import Resource
from alembic.database import db_session
from alembic.models import Owner, Owner, Problem, Device
from schemas import OwnerSchema, DeviceSchema
from marshmallow.exceptions import ValidationError 
from custom import json_error, errs

owner_schema = OwnerSchema()
device_schema = DeviceSchema()

class OwnersAPI(Resource):
    def get(self):
        owners=Owner.query.all()
        return owner_schema.dump(owners, many=True), 200
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
            
        owner = Owner.query.get(json_data.get('ownerid', None)) 
        if owner:
            return errs.exists
        
        
        try:
            data = owner_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Created user.", "user": json_data}

    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
            
        owner = Owner.query.get(json_data.get('ownerid', None)) 
        if not owner:
            return errs.not_found
        
        try:
            data = owner_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return {"message": "Updated user.", "user": json_data}

class OwnerAPI(Resource):
    def get(self, username):
        owner=Owner.query.filter_by(username=username).first()
        if not owner:
            return errs.not_found
        return owner_schema.dump(owner), 200
    
    def delete(self, username):
        owner=Owner.query.filter_by(username=username).first()
        if not owner:
            return errs.not_found
        db_session.delete(owner)
        db_session.commit()
        return '', 204

class OwnerDeviceAPI(Resource):
    def get(self, username):
        owner=Owner.query.filter_by(username=username).first()
        if not owner:
            return errs.not_found
        
        
        return {'owner':owner_schema.dump(owner), 'devices' : device_schema.dump(owner.device, many=True)}, 200
    