from flask import Flask, render_template, session
from flask_socketio import SocketIO
import requests

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)


@app.route('/')
def index():
    data = ["Value 1"]
    return render_template("index.html", data=data)

@socketio.on('connect', namespace='/fan')
def connect(mes):
    url = 'http://127.0.0.1:7788/get_fan'
    # headers = {'Content-type': 'text/html; charset=UTF-8'}
    data = {'fan_id' : fan.dfdf}
    response = requests.post(url, data=mes['fan_id'])
    socketio.emit('response', response)



if __name__ == '__main__':
    # app.run(port=5566, debug=True)
    socketio.run(app, host='0.0.0.0', port=5566, use_reloader=False)
