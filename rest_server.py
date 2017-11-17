#!/usr/bin/python
import logging
import socket

from flask import Flask
from flask import json
from flask import request

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

app = Flask(__name__)

port = 10000


@app.route('/upload/', methods=['POST'])
def api_upload():
    global sock_c
    response = request.data
    # ignore sensor stats from esc
    if 'sensorMeasurement' in response:
        return "200"
    #data = json.dumps(response)
    sock_c.sendall(response)
    return "200"


def create_socket():
    global sock_c
    # create a TCP/IP socket
    sock_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect the socket to the port where esc monitor is listening
    server_address = ('localhost', port)
    logging.info('connecting to %s port %s' % server_address)
    while True:
        try:
            sock_c.connect(server_address)
            break
        except ValueError:
            log.debug("connection error: keep re-trying...")
            continue


if __name__ == '__main__':
    logging.debug("Created rest server handler")
    create_socket()
    app.run(host='100.61.0.1', port=8080, threaded=False)
