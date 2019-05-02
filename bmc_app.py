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


app = Flask(__name__)
socketio = SocketIO(app)

# Global values
thread = None
threadRunning = False
sp = None

input_queue = [multiprocessing.Queue() for _ in range(config.NODE_NUM)]
output_queue = [multiprocessing.Queue() for _ in range(config.NODE_NUM)]

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


# Console
@socketio.on('connect', namespace='/console')
def connect():
    global thread
    global threadRunning

    if thread is None:
        threadRunning = True
        thread = Thread(target=send_console_message)
        thread.start()

    print("[Socket_Console] Connected")
    emit("response", {"data": "[Socket_Console] Connected"})

    # result = runPowerTool(['consolestat'])
    # result1 = result.split('\n')[0].split(':')[1]
    # result2 = result.split('\n')[1].split(':')[1]
    # socketio.emit("setting", {'node1':result1, 'node2':result2}, namespace='/console')


@socketio.on('disconnect', namespace='/console')
def disconnect():
    global thread
    global threadRunning

    if thread is not None:
        threadRunning = False
        thread = None

    print("[Socket_Console] Disconnected")


@socketio.on("send", namespace='/console')
def send(data):
    node_number = data["node_number"]
    cmd = data["cmd"] + "\n"

    input_queue[node_number].put(cmd.encode("UTF-8"))


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


# @socketio.on('input', namespace='/console')
# def console_input(message):
#     #print('input:' + str(message['node']) + message['data'].encode("utf-8"))
#     input_queue[message['node']].put(message['data'].encode("UTF-8"))

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


# Send console messages
def send_console_message():
    global output_queue
    global threadRunning
    global sp

    while threadRunning:
        time.sleep(0.001)
        for node_number in range(config.NODE_NUM):
            if not output_queue[node_number].empty():
                message_ = output_queue[node_number].get()
                # print("send: " + message)

                socketio.emit("receive", {"node_number": node_number, "message": message_}, namespace='/console')
                eventlet.sleep(0)

        if not sp.is_alive():
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


def init_serial_communication():
    global sp
    global input_queue
    global output_queue

    sp = serialworker.SerialProcess(input_queue, output_queue)
    sp.daemon = True
    sp.start()
    print("> Completed running serial process")


# Before running app, configure settings
def activate_app():
    print("> Start setting configures ...")
    init_db()
    init_serial_communication()
    print("> Finished setting configures ...")


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    activate_app()

    print("[ Starting server with {}://{}:{} ]".format(config.PROTOCOL, config.HOST, config.PORT))
    socketio.run(app, host=config.HOST, port=config.PORT, use_reloader=False, debug=True)
