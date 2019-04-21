# configuration
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, session, Response, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy, inspect

import requests, json
import config
import multiprocessing
import os
import time
import subprocess
import serialworker
from threading import Thread

# global value

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)
thread = None
threadRunning = False
sp = None

input_queue = [multiprocessing.Queue(), multiprocessing.Queue()]
output_queue = [multiprocessing.Queue(), multiprocessing.Queue()]

# DB
"""
@TODO
> Change sqlite3 -> 'something'
"""
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Should change it

db = SQLAlchemy(app)

# console part

def runPowerTool(args):
    '''
    @TODO
    '''
    # cmd = ['/usr/bin/powertool'] + args
    # fd = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
    # data = fd.read()
    # fd.close()
    # return data

class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.String(20), unique=True)
    user_pw = db.Column(db.String(30))
    position = db.Column(db.String(15))
    email = db.Column(db.String(50))

    def __init__(self, user_id, user_pw, position, email):
        self.user_id = user_id
        self.user_pw = user_pw
        self.position = position
        self.email = email

    def __repr__(self):
        return "id : {}, user_id : {}, position : {}, email : {}" \
            .format(self.id, self.user_id, self.position, self.email)


@app.route('/')
def index():
    data = ["Value 1"]
    return render_template("index.html", data=data)


@app.route('/account/get_account_data', methods=["POST"])
def get_account_data():
    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]
    result_dict = dict()

    data = db.session.query(Account).filter(Account.user_id == user_id).filter(Account.user_pw == user_pw).one()

    result_dict["user_id"] = data.user_id
    result_dict["user_pw"] = data.user_pw
    result_dict["position"] = data.position
    result_dict["email"] = data.email

    json_data = json.dumps(result_dict)

    return Response(json_data, status=200, mimetype="application/json")


@app.route('/account/create_account', methods=["POST"])
def create_account():
    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]
    email = request.form["email"]

    db.session.add(Account(user_id=user_id, user_pw=user_pw, position="user", email=email))

    json_data = json.dumps({"State": "OK"})
    return Response(json_data, status=200, mimetype="application/json")


'''
Socket IO
'''
# Fan
@socketio.on('connect', namespace='/fan')
def connect():
    print("[Socket_Fan] Connected")
    emit("response", {"data": "[Socket_Fan] Connected"})


@socketio.on('disconnect', namespace='/fan')
def disconnect():
    print("[Socket_FaN] Disconnected")


@socketio.on('message', namespace='/fan')
def message(data):
    print(data)
    emit("response", {"data": "[Socket_Fan] {}".format(data)})


@socketio.on('set_fan_speed', namespace='/fan')
def set_fan_speed(data):
    headers = dict()
    form_data = dict()
    url = "{}://{}:{}/{}/{}/".format(config.INTERPRETER_PROTOCOL,
                                     config.INTERPRETER_HOST,
                                     config.INTERPRETER_PORT,
                                     config.INTERPRETER_NAME,
                                     config.CATEGORY_FAN)
    url += "set_speed"

    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Accept'] = 'application/json'
    form_data['fan_number'] = data["fan_number"]
    form_data['speed'] = data["speed"]

    response = requests.post(url, headers=headers, data=form_data)
    res_data = json.loads(response.text)

    emit("response", res_data)


@socketio.on('set_fan_mode', namespace='/fan')
def set_fan_mode(data):
    headers = dict()
    form_data = dict()
    url = "{}://{}:{}/{}/{}/".format(config.INTERPRETER_PROTOCOL,
                                     config.INTERPRETER_HOST,
                                     config.INTERPRETER_PORT,
                                     config.INTERPRETER_NAME,
                                     config.CATEGORY_FAN)
    url += "set_auto_switch"

    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Accept'] = 'application/json'
    form_data['fan_auto_switch'] = data["fan_auto_switch"]

    response = requests.post(url, headers=headers, data=form_data)
    res_data = json.loads(response.text)

    emit('response', res_data)


# Sensor
@socketio.on('connect', namespace='/sensor')
def connect():
    print("[Socket_Sensor] Connected")
    emit("response", {"data": "[Socket_Sensor] Connected"})


@socketio.on('disconnect', namespace='/sensor')
def disconnect():
    print("[Socket_Sensor] Disconnected")


@socketio.on('message', namespace='/sensor')
def message(data):
    print(data)
    emit("response", {"data": "[Socket_Sensor] {}".format(data)})


@socketio.on('get_all_data', namespace='/sensor')
def get_all_data():
    url = "{}://{}:{}/{}/{}/".format(config.INTERPRETER_PROTOCOL,
                                     config.INTERPRETER_HOST,
                                     config.INTERPRETER_PORT,
                                     config.INTERPRETER_NAME,
                                     config.CATEGORY_SENSOR)
    url += "get_all_data"

    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    res_data = json.loads(response.text)

    emit('response', res_data)

# console
@socketio.on('connect', namespace='/term')
def connect():
    global thread
    global threadRunning
    print('term-socket : connected')
    if thread is None:
        threadRunning = True
        thread = Thread(target=checkQueue)
        thread.start()
    '''
    @TODO
    > after develope runPowerTool funtion
    '''
    # result = runPowerTool(['consolestat'])
    # result1 = result.split('\n')[0].split(':')[1]
    # result2 = result.split('\n')[1].split(':')[1]
    # socketio.emit("setting", {'node1':result1, 'node2':result2}, namespace='/term')

@socketio.on('setting', namespace='/term')
def term_setup(message):
    '''
    @TODO
    >> after develop runPowerTool funtion
    >> after define data dictionary
    '''
    # print(str(message['node']) + ":" + message['cmd'].encode("utf-8"));
    # n = message['node']
    # if n == 0 or n == 1:
    #     node = str(n+1)
    #     cmd = message['cmd'].encode("utf-8")
    #     if cmd == 'on':
    #         runPowerTool(['consoleon', node])
    #     elif cmd == 'off':
    #         runPowerTool(['consoleoff', node])
    # result = runPowerTool(['consolestat'])
    # result1 = result.split('\n')[0].split(':')[1]
    # result2 = result.split('\n')[1].split(':')[1]
    # socketio.emit("setting", {'node1':result1, 'node2':result2}, namespace='/term')

@socketio.on('disconnect', namespace='/term')
def disconnect():
    global thread
    global threadRunning
    if thread is not None:
        threadRunning = False
        thread = None

@socketio.on('input', namespace='/term')
def term_input(message):
    #print('input:' + str(message['node']) + message['data'].encode("utf-8"))
    input_queue[message['node']].put(message['data'].encode("UTF-8"))

# # power controll
# @socketio.on('handle', namespace='/pw')
# def handle(mes):
#     url = config.INTERPRETER_URI + '/run_power_tool'
#     # headers = {'Content-type': 'text/html; charset=UTF-8'}
#     data = {'tag': 'on'}
#
#     """
#     @TODO
#     > Modify these
#     """
#     # response = requests.post(url, data=mes)
#     print(mes)
#     response = requests.post(url, data=data)
#     socketio.emit('response', response)


def init_db():
    # Drop tables
    ins = inspect(db.engine)

    table_list = ins.get_table_names()
    if table_list is not None:
        print("> Tables in DB are exist")

    for table in table_list:
        if table == "account":
            Account.__table__.drop(db.engine)
            print("> Completed deleting the table, 'Account'")

    # Create tables
    db.create_all()
    print("> Completed creating tables")

    # Insert dummy data to db
    db.session.add(
        Account(user_id=config.ADMIN_USER_ID, user_pw=config.ADMIN_USER_PW, position="admin", email=config.ADMIN_EMAIL)
    )
    db.session.add(Account(user_id="test", user_pw="test", position="test", email="test@test.com"))

    db.session.commit()
    print("> Completed inserting dummy data to db")


# Before running app, configure settings
def activate_app():
    print("> Start setting configures ...")
    init_db()
    print("> Finished setting configures ...")

# console check
def checkQueue():
    global threadRunning
    while threadRunning:
        time.sleep(0.001)
        for node in range(2):
            if not output_queue[node].empty():
                message = output_queue[node].get()
                #print("send: " + message)
                socketio.emit("output", {'node':node,'buf':message}, namespace='/term')
                eventlet.sleep(0)
        if not sp.is_alive():
            break

if __name__ == '__main__':
    activate_app()
    # app.run(port=9001, debug=True)

    # serial Communication
    # sp = serialworker.SerialProcess(input_queue, output_queue)
    # sp.daemon = True
    # sp.start()

    print("[ Server starting with http://{}:{} ]".format(config.HOST, config.PORT))
    socketio.run(app, host=config.HOST, port=config.PORT, use_reloader=True, debug=True)
