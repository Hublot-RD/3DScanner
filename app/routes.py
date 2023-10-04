from flask import render_template
from app import app, socketio
from app.backend.scanner3d_backend import Scanner3D_backend
from threading import Thread, Event
import time



HOMEPAGE_TEMPLATE = 'test0.html'

# Create backend object and necessary objects
backend = Scanner3D_backend()
status_updator_thd_obj = Thread()
status_updator_thd_stop = Event()

# Create thread objects for dummy demonstration
# stop_capture_event = Event()
stop_image_event = Event()
# main_thread_obj = Thread()
image_thread_obj = Thread()

# def main_thread(thread_stop_event: Event()):
#     texts = ["Processing", "Processing.", "Processing..", "Processing..."]
#     cnt = 0
#     info = {'progress_value': 0, 'text_value': texts[cnt]}

#     while not thread_stop_event.is_set():
#         cnt += 1
#         info['progress_value'] = cnt % 101
#         info['text_value'] = texts[cnt%4]
#         socketio.emit('update_progress', info)
#         time.sleep(0.3)

#     # Closing thread properly
#     print('main_thread is closing')

def status_updator_thd_target(stop_event: Event()) -> None:
    while not stop_event.is_set():
        status = backend.get_status()
        socketio.emit('update_progress', status)
        time.sleep(0.5)
    
    # Closing thread properly
    print('status_updator_thd stopped')

def image_thread(thread_stop_event: Event()):
    image_number = 0

    while not thread_stop_event.is_set():
        number = image_number % 180
        socketio.emit('update_image', {'imageName': 'frame_{0:03}.jpg'.format(number)})
        image_number += 10
        time.sleep(0.5)
    
    # Closing thread properly
    print('image_thread is closing')
    


@app.route('/')
def index():
    # Serve the HTML page
    return render_template(HOMEPAGE_TEMPLATE)

@socketio.on('start_capture')
def handle_start_capture(data):
    backend.start(capture_params=data)

    # Activate status update
    global status_updator_thd_obj
    if not status_updator_thd_obj.is_alive():
        status_updator_thd_stop.clear()
        status_updator_thd_obj = Thread(target=status_updator_thd_target, kwargs={'stop_event': status_updator_thd_stop})
        status_updator_thd_obj.start()
   
    # Activate image update
    global image_thread_obj
    if not image_thread_obj.is_alive():
        stop_image_event.clear()
        image_thread_obj = Thread(target=image_thread, kwargs={'thread_stop_event': stop_image_event})
        image_thread_obj.start()


@socketio.on('stop_capture')
def handle_stop_capture():
    print('\nCapture stopped')

    # Stop backend
    backend.stop()

    # Stop status update
    status_updator_thd_stop.set()

    # Stop image update
    stop_image_event.set()
    image_thread_obj.join()

@socketio.on('light_toggled')
def handle_light_toggled(data):
    if data:
        print('Light turned ON')
    else:
        print('Light turned OFF')