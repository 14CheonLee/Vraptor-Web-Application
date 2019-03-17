import os
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

@app.route('/')
def hello_world():
    return "templete"



if __name__ == '__main__':
    app.run()