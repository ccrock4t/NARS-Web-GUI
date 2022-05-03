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
    GUI_PORT = int(lines[0].split("=")[1])
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
        data = dict(request.get_json()) # must convert to dict to read by key in javascript
        if path == APIkeys.PATH_INITIALIZE:
            socketio.emit('initialize', data)
            data = data[APIkeys.KEY_CONCEPTS] # get array of concepts
            socketio.emit('add_concept_nodes_to_memory_graph', list(data))
        elif path == APIkeys.PATH_UPDATE_BUFFER:
            socketio.emit('update_buffer', data)
        elif path == APIkeys.PATH_SHOW_CONCEPT_INFO:
            socketio.emit('show_concept_info', data)
        elif path == APIkeys.PATH_ADD_NEW_CONCEPTS:
            data = data[APIkeys.KEY_CONCEPTS] # get array of new concepts
            socketio.emit('add_concept_nodes_to_memory_graph', list(data))
        else:
            assert "ERROR: Path not handled in JavaScript"

        return jsonify({"Handled Post": "Request"})
    except Exception as e:
        print(e)
        return jsonify({"ERROR": request.path})


@app.route(APIkeys.PATH_INITIALIZE, methods=["POST"])
def initialize():
    return master_route(request)

@app.route(APIkeys.PATH_SHOW_CONCEPT_INFO, methods=["POST"])
def show_concept_info():
    return master_route(request)

@app.route(APIkeys.PATH_UPDATE_BUFFER, methods=["POST"])
def update_buffer():
    return master_route(request)

@app.route(APIkeys.PATH_ADD_NEW_CONCEPTS, methods=["POST"])
def add_new_concepts():
    return master_route(request)


"""

COMMAND TO NARS

"""
@socketio.on('get_initialize')
def get_initialize():
    """
        Get
    :param term_string:
    :return:
    """
    print('Getting NARS initialization info')
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.connect(('localhost', NARS_PORT))
    data = {APIkeys.COMMAND: APIkeys.COMMAND_GET_INITIALIZE}
    mysocket.send(json.dumps(data).encode())



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

@socketio.on('get_update_buffer')
def get_update_buffer(buffer_name):
    """
        Get
    :param term_string:
    :return:
    """
    print('Getting latest buffer info from NARS: ' + str(buffer_name))
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.connect(('localhost', NARS_PORT))
    data = {APIkeys.COMMAND: APIkeys.COMMAND_UPDATE_BUFFER,
            APIkeys.KEY_DATA: buffer_name}
    mysocket.send(json.dumps(data).encode())


@socketio.on('get_new_concepts')
def get_new_concepts():
    """
        Get
    :param term_string:
    :return:
    """
    print('Getting new concepts created in NARS')
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.connect(('localhost', NARS_PORT))
    data = {APIkeys.COMMAND: APIkeys.COMMAND_GET_NEW_CONCEPTS}
    mysocket.send(json.dumps(data).encode())


if __name__ == "__main__":
    app.run(port=GUI_PORT)