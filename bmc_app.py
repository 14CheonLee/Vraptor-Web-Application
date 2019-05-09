import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, session, Response, request, redirect
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy, inspect
from threading import Thread

import requests, json
import config
import multiprocessing
import os
import time
import subprocess
import serialworker


is_node_use = [False for _ in range(config.NODE_NUM)]

app = Flask(__name__)
socketio = SocketIO(app)

# Global values
thread_sensor = None
is_thread_sensor_running = False
thread_console = None
is_thread_console_running = False

serial_process = None
sensor_process = None

node_input_queue = [multiprocessing.Queue() for _ in range(config.NODE_NUM)]
node_output_queue = [multiprocessing.Queue() for _ in range(config.NODE_NUM)]
sensor_output_queue = multiprocessing.Queue()

# DB
"""
@TODO
> Change sqlite3 -> 'something'
"""
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Should change it

db = SQLAlchemy(app)


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
    if session.get("account_id") is not None:
        return render_template("index.html")
    else:
        return render_template("login.html")


@app.route('/account/login', methods=["POST"])
def login():
    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]

    try:
        record = db.session.query(Account).filter(Account.user_id == user_id).filter(Account.user_pw == user_pw).one()

        session["account_id"] = record.id
        session["user_id"] = record.user_id

        return redirect("/", code=302)

    except:
        return redirect("/", code=302)


@app.route('/account/logout', methods=["GET"])
def logout():
    session["account_id"] = None

    return redirect("/", code=302)


@app.route('/account/create', methods=["GET"])
def create():
    return render_template("create_account.html")


@app.route('/account/update', methods=["GET"])
def update():
    account_id = session["account_id"]
    account_data = dict()

    try:
        record = db.session.query(Account).filter(Account.id == account_id).one()

        account_data["user_id"] = record.user_id
        account_data["user_pw"] = record.user_pw
        account_data["position"] = record.position
        account_data["email"] = record.email

        return render_template("update_account.html", data=account_data)

    except:
        return render_template("error.html")


@app.route('/account/create_query', methods=["POST"])
def create_query():
    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]
    email = request.form["email"]

    try:
        db.session.add(Account(user_id=user_id, user_pw=user_pw, position="user", email=email))
        db.session.commit()

        return redirect("/", code=302)

    except:
        return redirect("/", code=302)


@app.route('/account/update_query', methods=["POST"])
def update_query():
    update_dict = dict()
    account_id = session["account_id"]

    update_dict["user_id"] = request.form["user_id"]
    update_dict["user_pw"] = request.form["user_pw"]
    update_dict["email"] = request.form["email"]

    try:
        db.session.query(Account).filter(Account.id == account_id).update(update_dict)
        db.session.commit()

        session["user_id"] = request.form["user_id"]

        return redirect("/", code=302)

    except:
        return redirect("/", code=302)


'''
Checking Power of Nodes
'''
def runPowerTool(args):
    '''
    @TODO
    '''
    # cmd = ['/usr/bin/powertool'] + args
    # fd = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
    # data = fd.read()
    # fd.close()
    # return data


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
    print("[Socket_Fan] Disconnected")


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
    global thread_sensor, is_thread_sensor_running

    if thread_sensor is None:
        is_thread_sensor_running = True
        thread_sensor = Thread(target=send_sensor_data)
        thread_sensor.start()

    print("[Socket_Sensor] Connected")
    emit("response", {"data": "[Socket_Sensor] Connected"})


@socketio.on('disconnect', namespace='/sensor')
def disconnect():
    global thread_sensor, is_thread_sensor_running

    if thread_sensor is not None:
        is_thread_sensor_running = False
        thread_sensor = None

    print("[Socket_Sensor] Disconnected")


@socketio.on('message', namespace='/sensor')
def message(data):
    print(data)
    emit("response", {"data": "[Socket_Sensor] {}".format(data)})


# Console
@socketio.on('connect', namespace='/console')
def connect():
    global thread_console, is_thread_console_running

    if thread_console is None:
        is_thread_console_running = True
        thread_console = Thread(target=send_console_message)
        thread_console.start()

    print("[Socket_Console] Connected")
    emit("response", {"data": "[Socket_Console] Connected"})

    # result = runPowerTool(['consolestat'])
    # result1 = result.split('\n')[0].split(':')[1]
    # result2 = result.split('\n')[1].split(':')[1]
    # socketio.emit("setting", {'node1':result1, 'node2':result2}, namespace='/console')


@socketio.on('disconnect', namespace='/console')
def disconnect():
    global thread_console, is_thread_console_running

    if thread_console is not None:
        is_thread_console_running = False
        thread_console = None

    print("[Socket_Console] Disconnected")


@socketio.on('send', namespace='/console')
def send(data):
    global node_input_queue

    node_number = data["node_number"]
    cmd = data["cmd"] + "\n"

    node_input_queue[node_number].put(cmd.encode("UTF-8"))


@socketio.on('check', namespace='/console')
def check(data):
    global is_node_use
    node_number = data["node_number"]

    # If somebody uses console
    if is_node_use[node_number] == True:
        emit("check_console", {"node_number": node_number, "is_use": is_node_use[node_number]})
    else:
        emit("check_console", {"node_number": node_number, "is_use": is_node_use[node_number]})

        is_node_use[node_number] = True


@socketio.on('close', namespace='/console')
def close(data):
    global is_node_use
    node_number = data["node_number"]

    is_node_use[node_number] = False


@socketio.on('setting', namespace='/console')
def console_setup(message):
    pass
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
    # socketio.emit("setting", {'node1':result1, 'node2':result2}, namespace='/console')


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


# Call sensor data
def call_sensor_data(output_queue):
    url = "{}://{}:{}/{}/{}/".format(config.INTERPRETER_PROTOCOL,
                                     config.INTERPRETER_HOST,
                                     config.INTERPRETER_PORT,
                                     config.INTERPRETER_NAME,
                                     config.CATEGORY_SENSOR)
    url += "get_all_data"

    headers = {'Accept': 'application/json'}

    while True:
        time.sleep(config.SENSOR_DATA_CALL_TIME)

        response = requests.get(url, headers=headers)
        res_data = json.loads(response.text)

        output_queue.put(res_data)


# Send console messages
def send_console_message():
    global node_output_queue, is_thread_console_running, serial_process

    while is_thread_console_running:
        time.sleep(config.CONSOLE_READ_TIME)
        for node_number in range(config.NODE_NUM):
            if not node_output_queue[node_number].empty():
                message_ = node_output_queue[node_number].get()
                # print("send: " + message)

                socketio.emit("receive", {"node_number": node_number, "message": message_}, namespace='/console')
                eventlet.sleep(0)

        if not serial_process.is_alive():
            break


# Send sensor data
def send_sensor_data():
    global sensor_output_queue, is_thread_sensor_running, sensor_process

    while is_thread_sensor_running:
        time.sleep(config.SENSOR_DATA_SEND_TIME)

        if not sensor_output_queue.empty():
            sensor_data = sensor_output_queue.get()

            socketio.emit("response", sensor_data, namespace='/sensor')

        if not sensor_process.is_alive():
            break


# Initiate
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


def init_serial_process():
    global serial_process, node_input_queue, node_output_queue

    serial_process = serialworker.SerialProcess(node_input_queue, node_output_queue)
    serial_process.daemon = True
    serial_process.start()
    print("> Completed running serial process")


def init_sensor_process():
    global sensor_process, sensor_output_queue

    sensor_process = multiprocessing.Process(target=call_sensor_data, args=(sensor_output_queue, ))
    sensor_process.daemon = True
    sensor_process.start()
    print("> Completed running sensor process")


# Before running app, configure settings
def activate_app():
    print("> Start setting configures ...")
    init_db()
    init_sensor_process()
    init_serial_process()
    print("> Finished setting configures ...")


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    activate_app()

    print("[ Starting server with {}://{}:{} ]".format(config.PROTOCOL, config.HOST, config.PORT))
    socketio.run(app, host=config.HOST, port=config.PORT, use_reloader=False, debug=True)
