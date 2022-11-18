from flask import request, jsonify
from flask_restful import Resource
from alembic.database import db_session
from alembic.models import User, User, Problem, Device
from schemas import UserSchema, DeviceSchema
from marshmallow.exceptions import ValidationError
from custom import json_error, errs
from main import bcrypt, master_required, admin_required, get_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token

user_schema = UserSchema()
device_schema = DeviceSchema()


class UserLoginAPI(Resource):
    def post(self):
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        user = User.query.filter_by(username=username)[0]
        if not user:
            return json_error("User not found", 404)
        if user.password != password:
            return json_error("Invalid password", 403)

        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)


class UsersAPI(Resource):
    @admin_required()
    def get(self):
        users = User.query.all()
        users_data = user_schema.dump(users, many=True)
        for data in users_data:
            data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        return users_data, 200

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request

        user = User.query.get(json_data.get('userid', None))
        if user:
            return errs.exists

        try:
            data = user_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        roles = ['admin', 'master', 'client', None]
        if data.role not in roles:
            return json_error(f'Bad request. Invalid role. Must be one of these: {", ".join(roles[:-1])}', 400)

        if data.role == 'admin' or data.role == 'master':
            verify_jwt_in_request()
            claims = get_user()
            if claims.role != 'admin':
                return json_error("Forbidden. Only admins can assign roles", 403)
        db_session.add(data)
        db_session.commit()
        json_data['password'] = bcrypt.generate_password_hash(json_data['password']).decode('utf-8')
        return {"message": "Created user.", "user": json_data}

    @jwt_required()
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request

        user = User.query.get(json_data.get('userid', None))
        claims = get_user()
        role = claims.role
        if not user:
            return errs.not_found
        if claims.role != 'admin' and claims.userid != json_data.get('userid', None):
            return json_error("Forbidden. Clients can only update themselves.", 403)

        try:
            data = user_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        roles = ['admin', 'master', 'client', None]
        if data.role not in roles:
            return json_error(f'Bad request. Invalid role. Must be one of these: {", ".join(roles[:-1])}', 400)

        if data.role != None:
            if role != 'admin' and role != data.role:
                return json_error("Forbidden. Only admins can assign roles", 403)
        db_session.add(data)
        db_session.commit()

        return {"message": "Updated user.", "user": json_data}


class UserAPI(Resource):
    @jwt_required()
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.role != 'master' and claims.username != username:
            return json_error("Forbidden. Client can only get info about himself.", 403)
        data = user_schema.dump(user)
        data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        return data, 200

    @jwt_required()
    def delete(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.username != username:
            return json_error("Forbidden. Client can only delete himself.", 403)
        db_session.delete(user)
        db_session.commit()
        return '', 204


class UserDeviceAPI(Resource):
    @jwt_required()
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return errs.not_found
        claims = get_user()
        if claims.role != 'admin' and claims.role != 'master' and claims.username != username:
            return json_error("Forbidden. Clients can only get info of their own devices.", 403)
        if claims.role == 'master' and user.service_centerid != claims.service_centerid:
            return json_error("Forbidden. Master can only get info of his clients.", 403)
        data = user_schema.dump(user)
        data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        return {'user': data, 'devices': device_schema.dump(user.device, many=True)}, 200
