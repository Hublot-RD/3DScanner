from flask import Flask
from flask_socketio import SocketIO


def create_app():
    print('create app')
    app = Flask(__name__)

    app.config['SECRET_KEY'] = "1A37BbcCJh67"
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

    socketio = SocketIO(app, debug=False, ping_timeout=20)
    return app, socketio

app, socketio = create_app()

# Import routes and socket events here
from app import routes