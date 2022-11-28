from flask import request
from flask_restful import Resource
from alembic.database import db_session
from alembic.models import Service_Center, User, Problem, Device, deviceStatus
from schemas import ServiceCenterSchema
from marshmallow.exceptions import ValidationError
from custom import json_error, errs
from main import bcrypt, master_required, admin_required, get_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token

service_schema = ServiceCenterSchema()


class ServicesAPI(Resource):

    def get(self):
        services = Service_Center.query.all()
        return service_schema.dump(services, many=True), 200

    # @admin_required()
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        service = Service_Center.query.get(json_data.get('serviceid', None))
        if service:
            return errs.exists
        try:
            data = service_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        db_session.add(data)
        db_session.commit()

        return {"message": "Created service.", "service": json_data}

    @master_required()
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        service = Service_Center.query.get(json_data.get('serviceid', None))
        if not service:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.service_centerid != json_data.get(
                'serviceid', None):
            return json_error("Forbidden. Only master can update info on their service.", 403)
        try:
            data = service_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        db_session.add(data)
        db_session.commit()

        return {"message": "Updated service.", "service": json_data}


class ServiceAPI(Resource):
    def get(self, serviceid):
        service = Service_Center.query.get(serviceid)
        if not service:
            return errs.not_found
        return service_schema.dump(service), 200

    @admin_required()
    def delete(self, serviceid):
        service = Service_Center.query.get(serviceid)
        if not service:
            return errs.not_found
        db_session.delete(service)
        db_session.commit()
        return '', 204


class ServiceDeviceAPI(Resource):
    @admin_required()
    def get(self):
        statuses = [e.name for e in deviceStatus] + [None]
        result = {}

        for status in statuses:
            result[status] = len(Device.query.filter_by(status=status).all())
        return result, 200
