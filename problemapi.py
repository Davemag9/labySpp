from flask import request
from flask_restful import Resource
from alembic.database import db_session
from alembic.models import Service_Center, User, Problem, Device, branchEnum
from schemas import ProblemSchema
from marshmallow.exceptions import ValidationError
from custom import json_error, errs
from main import bcrypt, master_required, admin_required, get_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token

problem_schema = ProblemSchema()


class ProblemsAPI(Resource):
    @jwt_required()
    def get(self):
        problems = Problem.query.all()
        return problem_schema.dump(problems, many=True), 200

    @master_required()
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        problem = Problem.query.get(json_data.get('problemid', None))
        if problem:
            return errs.exists
        try:
            data = problem_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        db_session.add(data)
        db_session.commit()
        return {"message": "Created problem.", "problem": json_data}

    @admin_required()
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        problem = Problem.query.get(json_data.get('problemid', None))
        if not problem:
            return errs.not_found
        try:
            data = problem_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        db_session.add(data)
        db_session.commit()

        return {"message": "Updated problem.", "problem": json_data}


class ProblemAPI(Resource):
    @jwt_required()
    def get(self, problemid):
        problem = Problem.query.get(problemid)
        if not problem:
            return errs.not_found
        return problem_schema.dump(problem), 200

    @admin_required()
    def delete(self, problemid):
        problem = Problem.query.get(problemid)
        if not problem:
            return errs.not_found
        db_session.delete(problem)
        db_session.commit()
        return '', 204


class ProblemBranchAPI(Resource):
    @jwt_required()
    def get(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        branch = json_data.get('branch', None)
        branchEnums = [e.name for e in branchEnum]
        if branch not in branchEnums:
            return json_error('Invalid request. Bad status value. Must be on of: ' + ', '.join(branchEnums), 400)
        problems = Problem.query.filter_by(branch=branch)
        return problem_schema.dump(problems, many=True), 200
