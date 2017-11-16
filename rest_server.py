#!/usr/bin/python
import socket

from flask import Flask
from flask import request

import logmanager as log
import snmp_stat as rest_obj

app = Flask(__name__)

port = 10000


@app.route('/upload/', methods=['POST'])
def api_upload():
    response = request.data
    # ignore sensor stats from esc
    if 'sensorMeasurement' in response:
        return "200"
    rest_obj.snmp_handler_response(response)
    return "200"


def create_socket():
    # create a TCP/IP socket
    sock_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect the socket to the port where esc monitor is listening
    server_address = ('localhost', port)
    log.info('connecting to %s port %s' % server_address)
    while True:
        try:
            sock_c.connect(server_address)
            break
        except ValueError:
            log.debug("connection error: keep re-trying...")
            continue


def rest_server_handler():
    log.debug("Created rest server handler")
    create_socket()
    app.run(host='100.61.0.1', port=8080, threaded=True)
