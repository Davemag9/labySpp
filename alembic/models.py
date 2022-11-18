from sqlalchemy import create_engine, Column, Integer, String, Enum, orm, ForeignKey, Table, Enum
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, relationship
from .database import Base
import enum


class userStatus(enum.Enum):
    inactive = 0
    active = 1


class deviceStatus(enum.Enum):
    arrived = 0
    in_work = 1
    ready = 2


class branchEnum(enum.Enum):
    screen = 0
    battery = 1
    button = 2
    os = 3
    hardware = 4
    other = 5


class Service_Center(Base):
    __tablename__ = "service_center"
    serviceid = Column(Integer, primary_key=True)
    city = Column(String(45), nullable=False)
    adress = Column(String(45), nullable=False)
    phone = Column(String(45), nullable=False)
    rating = Column(String(45), nullable=True)

    def __repr__(self):
        return f'Service_Center(serviceid={self.serviceid},city={self.city},address={self.adress})'


class User(Base):
    __tablename__ = "user"
    userid = Column(Integer, primary_key=True)
    username = Column(String(45), nullable=False, unique=True)
    firstname = Column(String(45), nullable=True)
    lastname = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    password = Column(String(45), nullable=False)
    phone = Column(String(45), nullable=True)
    userStatus = Column(Enum(userStatus), default=userStatus.active, nullable=False)
    service_centerid = Column(Integer, ForeignKey(Service_Center.serviceid, ondelete="CASCADE"))
    service_center = orm.relationship(Service_Center, backref="owner")
    role = Column(String(32), default="client", nullable=False)

    def __repr__(self):
        return f'User(username={self.username},name={self.firstname + " " if self.firstname else ""}{self.lastname})'


class Problem(Base):
    __tablename__ = "problem"
    problemid = Column(Integer, primary_key=True)
    branch = Column(Enum(branchEnum), nullable=False)
    daysToSolve = Column(Integer, nullable=True)

    def __repr__(self):
        return f'Problem(problemid={self.problemid})'


class Device(Base):
    __tablename__ = "device"
    deviceid = Column(Integer, primary_key=True)
    firm = Column(String(45), nullable=False)
    model = Column(String(45), nullable=False)
    status = Column(Enum(deviceStatus), nullable=True)
    userid = Column(Integer, ForeignKey(User.userid, ondelete="CASCADE"))
    user = orm.relationship(User, backref="device")
    problems = relationship("Problem", secondary='problem_to_device', passive_deletes=True)

    def __repr__(self):
        return f'Device(deviceid={self.deviceid},firm={self.firm},model={self.model})'


problem_to_device = Table(
    "problem_to_device",
    Base.metadata,
    Column("problemid", ForeignKey("problem.problemid", ondelete="CASCADE")),
    Column("deviceid", ForeignKey("device.deviceid", ondelete="CASCADE"))
)
