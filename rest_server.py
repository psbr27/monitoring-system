#!/usr/bin/python
from flask import Flask
from flask import json
from flask import request

import socket
import sys
import time

import snmp_stat as snmpStat

app = Flask(__name__)



@app.route('/')
def index():
            return "Hello, world!"

@app.route('/upload/', methods = ['POST'])
def api_upload():
    global sock_c
    response = request.data
    if 'sensorMeasurement' in response:
    	return "200"
    print(response)
    print("--------------> \n")
    #data = json.dumps(response).encode('utf-8') 
    #sock_c.sendall(response)
    snmpStat.handle_response(response)
    return "200"

def create_socket():
    global sock_c
# create a TCP/IP socket
    sock_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#onnect the socket to the port where esc monitor is listening
    server_addr = ('localhost', 10000)
    print >>sys.stderr, 'connecting to %s port %s' %server_addr
    while True:
        try:
            sock_c.connect(server_addr)
            break
        except:
            print("connection error: keep re-trying...")
            time.sleep(2)
            continue


def rest_server_hdlr():
    print("Created rest server handler")
    create_socket()
    app.run(host='100.61.0.1', port=8080, threaded=True)


