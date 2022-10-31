from models import Session, Device, Owner, Service_Center, Problem, problem_to_device
session=Session()

device = Device(deviceid=1, firm='Apple', model='IPHONE 10', ownerid=1)
device1 = Device(deviceid=2, firm='Samsung', model='Galaxy S21', ownerid=2)
owner = Owner(ownerid=1, username='user123', lastname='Kovaliv', email='kovaliv@gmail.com', password='45765')
owner1 = Owner(ownerid=2, username='user000', lastname='Vasyliv', email='vas356@gmail.com', password='876765')
service = Service_Center(serviceid=1, city='Kalush', adress='ertyu678', phone='098463893', rating='3.8')
service1 = Service_Center(serviceid=2, city='Kalush', adress='998', phone='096398793', rating='4.8')
problem = Problem(problemid=1, branch='some branch', daysToSolve=5)
problem1 = Problem(problemid=2, branch='some branch', daysToSolve=9)
device1.problems.append(problem)
device1.problems.append(problem1)



session.add(device)
session.add(device1)
session.add(owner)
session.add(owner1)
session.add(service)
session.add(service1)



session.commit()