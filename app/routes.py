from flask import render_template, send_from_directory
from app import app, socketio
from app.backend.scanner3d_backend import Scanner3D_backend
from threading import Thread, Event
from queue import Queue
import time


# HOMEPAGE_TEMPLATE = 'test0.html'
HOMEPAGE_TEMPLATE = 'index.html'

# Create backend object and necessary objects
status_queue = Queue()
backend = Scanner3D_backend(status_queue=status_queue)
status_updator_thd_obj = Thread()

def status_updator_thd_target() -> None:
    '''
    Continuously updates the status of the capture process.
    '''
    while True:
        if not status_queue.empty():
            status = status_queue.get()
            socketio.emit('update_progress', status)
        time.sleep(0.1)
    
    # Closing thread properly
    print('status_updator_thd stopped')

@app.route('/')
# @socketio.on('/')
def index():
    # Activate status update
    global status_updator_thd_obj
    if not status_updator_thd_obj.is_alive():
        status_updator_thd_obj = Thread(target=status_updator_thd_target, daemon=True)
        status_updator_thd_obj.start()
    # Serve the HTML page
    return render_template(HOMEPAGE_TEMPLATE)


@app.route('/cam_imgs/<filename>')
def serve_image(filename):
    return send_from_directory('static/cam_imgs', filename)

@socketio.on('refresh_preview')
def handle_refresh_preview():
    file_name = backend.refresh_image()
    socketio.emit('update_image', {'filename': file_name})
    # pass

@socketio.on('refresh_usb_list')
def handle_refresh_preview():
    device_list = backend.refresh_usb_list()
    socketio.emit('update_usb_list', {'device_list': device_list})
    # pass

@socketio.on('start_capture')
def handle_start_capture(data):
    backend.start(capture_params=data)
    # pass

@socketio.on('stop_capture')
def handle_stop_capture():
    print('stop_capture received')
    # Stop backend
    backend.stop()

@socketio.on('ok_capture')
def handle_ok_capture():
    print('ok_capture received')
    # Stop backend
    backend.stop()
