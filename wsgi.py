# from app import create_app
from app import app, socketio

if __name__ == '__main__':
    # Run the Flask-SocketIO application for development
    print("Running in debug mode")
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
else:
    # Run the Flask-SocketIO application for production
    print("Running in production mode")
