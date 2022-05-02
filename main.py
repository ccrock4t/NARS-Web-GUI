import json
import socket

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Lock

import APIkeys


"""
START SERVER
"""

async_mode = None

app = Flask(__name__)
app.secret_key = "mostsecretbarnone"
socketio = SocketIO(app, async_mode=async_mode,cors_allowed_origins="*")
thread = None
thread_lock = Lock()

# get port
with open("config.cfg") as cfg:
    lines = cfg.readlines()
    NARS_PORT = int(lines[1].split("=")[1])

"""

GUI Webpage routing

"""

@app.route('/')
def index():
    return redirect(url_for('NARS_view'))


@app.route('/main/')
def NARS_view():
    return render_template('index.html', async_mode=socketio.async_mode)

"""

POST API for GUI

"""

def master_route(request):
    path = request.path
    print('Got HTTP ' + request.method + ' request ' + str(path))
    try:
        data = dict(request.get_json())
        if path == APIkeys.PATH_INITIALIZE:
            # todo hide a loading screen, show the GUI elements
            socketio.emit('initialize', data)
        elif path == APIkeys.PATH_ADD_CONCEPT:
            socketio.emit('add_node_to_memory_graph', data)
        elif path == APIkeys.PATH_ADD_LINK:
            socketio.emit('add_link', data)
        elif path == APIkeys.PATH_ADD_TASK_TO_BUFFER:
            socketio.emit('add_task_to_buffer', data)
        elif path == APIkeys.PATH_REMOVE_TASK_FROM_BUFFER:
            socketio.emit('remove_task_from_buffer', data)
        elif path == APIkeys.PATH_SHOW_CONCEPT_INFO:
            socketio.emit('show_concept_info', data)
        else:
            assert "ERROR: Path not handled in JavaScript"

        return jsonify({"hello": "world"})
    except Exception as e:
        print(e)
        return jsonify({"ERROR": request.path})


@app.route(APIkeys.PATH_INITIALIZE, methods=["POST"])
def initialize():
    return master_route(request)


@app.route(APIkeys.PATH_ADD_CONCEPT, methods=["POST"])
def add_concept():
    return master_route(request)

@app.route(APIkeys.PATH_SHOW_CONCEPT_INFO, methods=["POST"])
def show_concept_info():
    return master_route(request)

@app.route(APIkeys.PATH_ADD_LINK, methods=["POST"])
def add_link():
    return master_route(request)


@app.route(APIkeys.PATH_ADD_TASK_TO_BUFFER, methods=["POST"])
def add_task_to_buffer():
    return master_route(request)


@app.route(APIkeys.PATH_REMOVE_TASK_FROM_BUFFER, methods=["POST"])
def remove_task_from_buffer():
    return master_route(request)


"""

COMMAND TO NARS

"""
# Receive the test request from client and send back a test response
@socketio.on('send_input')
def send_input(input_string):
    print('Sending input to NARS: ' + str(input_string))
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.connect(('localhost', NARS_PORT))
    data = {APIkeys.COMMAND: APIkeys.COMMAND_INPUT,
                   APIkeys.KEY_DATA: input_string}
    mysocket.send(json.dumps(data).encode())

@socketio.on('get_concept_info')
def get_concept_info(term_string):
    """
        Get
    :param term_string:
    :return:
    """
    print('Getting latest concept info from NARS: ' + str(term_string))
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.connect(('localhost', NARS_PORT))
    data = {APIkeys.COMMAND: APIkeys.COMMAND_GET_CONCEPT_INFO,
            APIkeys.KEY_DATA: term_string}
    mysocket.send(json.dumps(data).encode())



if __name__ == "__main__":
    app.run()