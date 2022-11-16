from alembic.models import Service_Center, Owner, Problem, Device, deviceStatus, branchEnum, userStatus
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_enum import EnumField


class ServiceCenterSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Center
        # include_relationships = True
        load_instance = True
        include_fk = True

class OwnerSchema(SQLAlchemyAutoSchema):
    userStatus = EnumField(userStatus)
    class Meta:
        model = Owner
        # include_relationships = True
        load_instance = True
        include_fk = True
        exclude = ("password",)
    password = auto_field(load_only=True)
    
class ProblemSchema(SQLAlchemyAutoSchema):
    branch = EnumField(branchEnum)
    class Meta:
        model = Problem
        # include_relationships = True
        load_instance = True
        include_fk = True

class DeviceSchema(SQLAlchemyAutoSchema):
    status = EnumField(deviceStatus)

    class Meta:
        model = Device
        # include_relationships = True
        load_instance = True
        include_fk = True



