from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)


@app.route('/')
def hello_world():
    data = ["Value 1"]
    return render_template("index.html", data=data)


if __name__ == '__main__':
    app.run(port=5566, debug=True)
