from flask import Flask, render_template, session, Response, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy, inspect

import requests, json
import config

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

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
socket IO
'''

# fan controll

@socketio.on('connect', namespace='/fan')
def connect(mes):
    url = config.INTERPRETER_URI + '/get_fan_mode'
    # headers = {'Content-type': 'text/html; charset=UTF-8'}
    data = {'fan_id': 1}

    """
    @TODO
    > Modify these
    """
    # response = requests.post(url, data=mes)
    print(mes)
    response = requests.post(url, data=data)
    socketio.emit('response', response)

@socketio.on('set', namespace='/fan')
def set(mes):
    url = config.INTERPRETER_URI + '/set_fan_mode'
    # headers = {'Content-type': 'text/html; charset=UTF-8'}
    data = {'fan_id': 1, 'fan_mode':2}

    """
    @TODO
    > Modify these
    """
    # response = requests.post(url, data=mes)
    print(mes)
    response = requests.post(url, data=data)
    socketio.emit('response', response)

# sensor controll

@socketio.on('connect', namespace='/sensor')
def connect(mes):
    url = config.INTERPRETER_URI + '/get_sensor_data'
    # headers = {'Content-type': 'text/html; charset=UTF-8'}
    data = {'node_num': 1}

    """
    @TODO
    > Modify these
    """
    # response = requests.post(url, data=mes)
    print(mes)
    response = requests.post(url, data=data)
    socketio.emit('response', response)

# power controll

@socketio.on('handle', namespace='/pw')
def handle(mes):
    url = config.INTERPRETER_URI + '/run_power_tool'
    # headers = {'Content-type': 'text/html; charset=UTF-8'}
    data = {'tag': 'on'}

    """
    @TODO
    > Modify these
    """
    # response = requests.post(url, data=mes)
    print(mes)
    response = requests.post(url, data=data)
    socketio.emit('response', response)

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


# Before run app, configuring settings
def activate_app():
    print("> Start setting configures ...")
    init_db()
    print("> Finished setting configures ...")


if __name__ == '__main__':
    activate_app()
    # app.run(port=5566, debug=True)
    socketio.run(app, host='0.0.0.0', port=5566, use_reloader=False, debug=True)
    print("--- server start ---")
