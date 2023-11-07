# from app import create_app
from app import app, socketio
print('hey')
print('name:', __name__)


# Create the Flask application
# app, socketio = create_app()

if __name__ == '__main__':
    # Run the Flask-SocketIO application for development
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
