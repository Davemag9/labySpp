from schemas import *
from main import app, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

app.testing = True
client = app.test_client()


def check_data(responce_json, compare_object):
    for x in compare_object.keys():
        if x == 'password':
            continue
        else:
            assert responce_json[x] == compare_object[x]


global test_service_id, test_service_json
test_service_id = 'not found'
test_service_json = {
    'serviceid':1,
    'city':'Lviv',
    'adress':'Bandery',
    'phone':'+1234567890',
    'rating':'10'
}

global admin_token
admin_token = ''

def test_login_admin():
    global admin_token
    res = client.post(f'/api/v1/login' ,json={
        "username": 'admin',
        "password": 'admin'
    })
    assert res.status_code == 200
    admin_token=res.json["access_token"]

def test_create_service():
    global test_service_id, test_service_json
    res = client.post('/api/v1/service', json=test_service_json)
    assert res.status_code == 200
    check_data(res.json['service'], test_service_json)
    # assert res.json.get('serviceid')
    test_service_json = res.json["service"]

def test_create_service2():
    global test_service_id, test_service_json
    res = client.post('/api/v1/service', json=test_service_json)
    assert res.status_code == 403


global test_user_id
test_user_id = 'not found'
test_user_json = {
    'userid':1,
    'username':'usern',
    'firstname': 'John2',
    'lastname': 'Jam2es2',
    'email': 'joh2n.james.2022@email.com',
    'password': 'qwerty22022',
    'userStatus':"active",
    'service_centerid' : 1,
    "role":'master'
}

def authentication_headers(username = test_user_json['username']):
    return {'headers': {
            'Authorization': f'''Bearer {username}'''
        }
    }

def test_create_user():
    global test_user_json, admin_token
    res = client.post(f'/api/v1/user', json=test_user_json, **authentication_headers(admin_token))
    assert res.status_code == 200
    check_data(res.json['user'], test_user_json)

def test_create_user2():
    global test_user_json, admin_token
    res = client.post(f'/api/v1/user', json=test_user_json, **authentication_headers(admin_token))
    assert res.status_code == 403

global test_token
test_token = ''

def test_login_user():
    global test_user_json, test_token
    res = client.post(f'/api/v1/login' ,json={
        "username": test_user_json["username"],
        "password": test_user_json["password"]
    })
    assert res.status_code == 200
    test_token=res.json["access_token"]

def test_get_user():
    global admin_token
    res = client.get(f'/api/v1/user', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_service():
    global admin_token
    res = client.get(f'/api/v1/service', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_user_username():
    global test_user_json, test_token
    res = client.get(f'/api/v1/user/{test_user_json["username"]}', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_update_user():
    global test_user_json
    test_user_json['firstname'] = 'John3'
    res = client.put('/api/v1/user', json=test_user_json, **authentication_headers(test_token))
    assert res.status_code == 200
    check_data(res.json['user'], test_user_json)
    test_user_json['firstname'] = 'John2'
    res = client.put('/user', json=test_user_json, **authentication_headers(test_token))

def test_update_service():
    global test_service_json, admin_token
    test_user_json['adress'] = 'Chuprinki'
    res = client.put('/api/v1/service', json=test_service_json, **authentication_headers(admin_token))
    assert res.status_code == 200
    test_user_json['adress'] = 'Bandery'
    res = client.put('/service', json=test_service_json, **authentication_headers(admin_token))


def test_get_service_id():
    global test_service_id, admin_token
    res = client.get(f'/api/v1/service/{test_service_json["serviceid"]}', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_service_id1():
    global test_service_id, admin_token
    res = client.get(f'/api/v1/service/{test_service_json["serviceid"]+1}', **authentication_headers(admin_token))
    assert res.status_code == 404


global test_problem_id, test_problem_json
test_problem_id = 'not found'
test_problem_json = {
    'problemid':1,
    'branch':'screen',
    'daysToSolve':3
}

def test_create_problem():
    global test_problem_json, admin_token
    res = client.post('/api/v1/problem', json=test_problem_json, **authentication_headers(admin_token))
    assert res.status_code == 200

def test_create_proble3():
    global test_problem_json, admin_token
    res = client.post('/api/v1/problem', json=test_problem_json, **authentication_headers(admin_token))
    assert res.status_code == 403

def test_get_problem():
    global admin_token
    res = client.get(f'/api/v1/problem', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_update_problem():
    global test_problem_json, admin_token
    test_problem_json['branch'] = 'button'
    res = client.put('/api/v1/problem', json=test_problem_json, **authentication_headers(admin_token))
    assert res.status_code == 200
    test_problem_json['branch'] = 'screen'
    res = client.put('/problem', json=test_problem_json, **authentication_headers(admin_token))

def test_get_problem_id():
    global test_problem_json, admin_token
    res = client.get(f'/api/v1/problem/{test_problem_json["problemid"]}', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_problem_id1():
    global test_problem_json, admin_token
    res = client.get(f'/api/v1/problem/{test_problem_json["problemid"]+1}', **authentication_headers(admin_token))
    assert res.status_code == 404

global test_device_id, test_device_json
test_device_id = 'not found'
test_device_json = {
    'deviceid':1,
    'firm':'Samsung',
    'model':'S10',
    'status':'arrived',
    'userid':1
}

def test_create_device():
    global test_device_json, test_token
    res = client.post('/api/v1/device', json=test_device_json, **authentication_headers(test_token))
    assert res.status_code == 200

def test_create_device2():
    global test_device_json, test_token
    res = client.post('/api/v1/device', json=test_device_json, **authentication_headers(test_token))
    assert res.status_code == 403

def test_get_device():
    global admin_token
    res = client.get(f'/api/v1/device', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_update_device():
    global test_device_json, admin_token
    test_device_json['firm'] = 'LG'
    res = client.put('/api/v1/device', json=test_device_json, **authentication_headers(admin_token))
    assert res.status_code == 200
    test_device_json['firm'] = 'Samsung'
    res = client.put('/device', json=test_device_json, **authentication_headers(admin_token))

def test_get_device_status():
    global test_device_json, admin_token
    res = client.get(f'/api/v1/device/findByStatus', json = { "status":"arrived" },
                     **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_device_status1():
    global test_device_json, admin_token
    res = client.get(f'/api/v1/device/findByStatus', json = { "status":"arrrived" },
                     **authentication_headers(admin_token))
    assert res.status_code == 400

def test_get_device_firm():
    global test_device_json, admin_token
    res = client.get(f'/api/v1/device/findByFirm', json = { "firm":"Samsung" },
                     **authentication_headers(admin_token))
    assert res.status_code == 200



def test_get_device_id():
    global test_device_json, admin_token
    res = client.get(f'/api/v1/device/{test_device_json["deviceid"]}', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_device_problems():
    global test_device_json, admin_token
    res = client.get(f'/api/v1/device/{test_device_json["deviceid"]}/problem', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_user_devices():
    global test_user_json, test_token
    res = client.get(f'/api/v1/user/{test_user_json["username"]}/device', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_service_device():
    global admin_token
    res = client.get(f'/api/v1/service/device', **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_problem_branch():
    global test_problem_json, admin_token
    res = client.get(f'/api/v1/problem/findByBranch', json = { "branch":"screen" },
                     **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_problem_branch1():
    global test_problem_json, admin_token
    res = client.get(f'/api/v1/problem/findByBranch', json = { "branch":"screeen" },
                     **authentication_headers(admin_token))
    assert res.status_code == 400

def test_add_problem_device():
    global test_device_json, test_problem_json, admin_token
    res = client.post(f'/api/v1/device/{test_device_json["deviceid"]}/problem', json = test_problem_json,
                      **authentication_headers(admin_token))
    assert res.status_code == 200

def test_get_device_id_problem_id():
    global test_device_json, test_problem_json, admin_token
    res = client.get(f'/api/v1/device/{test_device_json["deviceid"]}/problem/{test_problem_json["problemid"]}',
                     **authentication_headers(admin_token))
    assert res.status_code == 200

def test_delete_problem_device():
    global test_device_json, test_problem_json, admin_token
    res = client.delete(f'/api/v1/device/{test_device_json["deviceid"]}/problem/{test_problem_json["problemid"]}',
                    **authentication_headers(admin_token))
    assert res.status_code == 204

def test_create_problem2():
    global test_problem_json, admin_token
    res = client.post('/api/v1/problem', json=test_problem_json, **authentication_headers(admin_token))
    assert res.status_code == 200

def test_update_device_problem():
    global test_service_json, test_problem_json, admin_token
    test_problem_json['daysToSolve'] = 1
    res = client.put(f'/api/v1/device/{test_device_json["deviceid"]}/problem/{test_problem_json["problemid"]}',
                     json=test_problem_json, **authentication_headers(admin_token))
    assert res.status_code == 200
    test_problem_json['daysToSolve'] = 3
    res = client.put('/service', json=test_service_json, **authentication_headers(admin_token))

def test_del_device1():
    global test_device_json,admin_token
    res = client.delete(f'/api/v1/device/{test_device_json["deviceid"]+1}', **authentication_headers(admin_token))
    assert res.status_code == 404

def test_del_device():
    global test_device_json,admin_token
    res = client.delete(f'/api/v1/device/{test_device_json["deviceid"]}', **authentication_headers(admin_token))
    assert res.status_code == 204

def test_del_service1():
    global test_service_id,test_token
    res = client.delete(f'/api/v1/service/{test_service_json["serviceid"]+1}', **authentication_headers(admin_token))
    assert res.status_code == 404

def test_del_service():
    global test_service_id,test_token
    res = client.delete(f'/api/v1/service/{test_service_json["serviceid"]}', **authentication_headers(admin_token))
    assert res.status_code == 204

def test_del_user1():
    global test_user_json, admin_token
    res = client.delete(f'/api/v1/user/Antoha', **authentication_headers(admin_token))
    assert res.status_code == 404

def test_del_user():
    global test_user_json, admin_token
    res = client.delete(f'/api/v1/user/{test_user_json["username"]}', **authentication_headers(admin_token))
    assert res.status_code == 204

def test_del_problem1():
    global test_problem_json,test_token
    res = client.delete(f'/api/v1/problem/{test_problem_json["problemid"]+1}', **authentication_headers(admin_token))
    assert res.status_code == 404

def test_del_problem():
    global test_problem_json,test_token
    res = client.delete(f'/api/v1/problem/{test_problem_json["problemid"]}', **authentication_headers(admin_token))
    assert res.status_code == 204