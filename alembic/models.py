from sqlalchemy import create_engine, Column, Integer, String, Enum, orm, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, relationship

DBURL = 'postgresql+psycopg2://postgres:pavliv1alina2@localhost/service_center'
engine=create_engine(DBURL)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

Base = declarative_base()



class Service_Center(Base):
    __tablename__="service_center"
    serviceid = Column(Integer, primary_key=True)
    city = Column(String(45), nullable=False)
    adress = Column(String(45), nullable=False)
    phone = Column(String(45), nullable=False)
    rating = Column(String(45), nullable=True)

class Owner(Base):
    __tablename__="owner"
    ownerid = Column(Integer, primary_key=True)
    username = Column(String(45), nullable=False, unique=True)
    firstname = Column(String(45), nullable=True)
    lastname = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    password = Column(String(45), nullable=False)
    phone = Column(String(45), nullable=True)
    userStatus = Column(String(45), nullable=True)
    service_centerid = Column(Integer, ForeignKey(Service_Center.serviceid, ondelete="CASCADE"))
    service_center = orm.relationship(Service_Center, backref="owner")

class Problem(Base):
    __tablename__ = "problem"
    problemid = Column(Integer, primary_key=True)
    branch = Column(String(45), nullable=False)
    daysToSolve = Column(Integer, nullable=True)

class Device(Base):
    __tablename__="device"
    deviceid = Column(Integer, primary_key=True)
    firm = Column(String(45), nullable=False)
    model = Column(String(45), nullable=False)
    status = Column(String(45), nullable=True)
    ownerid = Column(Integer, ForeignKey(Owner.ownerid, ondelete="CASCADE"))
    owner = orm.relationship(Owner, backref="device")
    problems = relationship("Problem", secondary='problem_to_device', passive_deletes=True)


problem_to_device = Table(
    "problem_to_device",
    Base.metadata,
    Column("problemid", ForeignKey("problem.problemid", ondelete="CASCADE")),
    Column("deviceid", ForeignKey("device.deviceid", ondelete="CASCADE"))
)