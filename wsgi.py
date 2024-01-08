# from app import create_app
from app import app, socketio

if __name__ == '__main__':
    # Run the Flask-SocketIO application for development
    print("Running in debug mode")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
else:
    # Run the Flask-SocketIO application for production
    print("Running in production mode")
