#!/usr/bin/env python
import json
import csv
import sys,time
import datetime
import time
from pathlib import Path
import pickle
import socket

interval=15
output_file = "esc_health_data_"
skip_header=True

#employee_data='{ "employee_details": [{ "employee_name": "James", "email": "james@gmail.com", "job_profile": "Sr. Developer" }, { "employee_name": "Smith", "email": "Smith@gmail.com", "job_profile": "Project Lead" } ] }'

#employee_data='{"bandIndex":0,"bandInfo":{"timeStampHealthCheck":10247.651355,"sensor":{"agcGain":59,"gpioOverLoad":0,"gpioSPIvalue":0,"rmsAverage":20.639767,"agcMaxVal":125,"noiseRssiDbm":-86.925903,"dcI":0,"dcQ":-5,"iqImbalanceGaindB":0,"iqImbalancePhaseDeg":0,"numDmaOverflows":0},"adiSettings":{"adiRxLoHz":3571503998,"adiTxLoHz":3571503998,"adiGainValue":59,"adiTxAttenutation":88000,"adiRxClockHz":49151999,"adiTxClockHz":49151999}},"hps":{"oneMinLoad":1,"memoryFreeKb":718712,"memoryTotalKb":763048,"upTime":10527,"cpuClockSpeed":0},"i2c":{"humidity":5.480957,"temperature":109.225098,"compass_x_axis":-3204,"compass_y_axis":2589,"compass_z_axis":4133,"compassChange":0}}'

def write_to_csv(json_file, output_file):
    global skip_header
    values=[]
    header=[]
#wait for the signal from esc_monit
    myFile = open(json_file, 'r')
    json_parsed = pickle.load(myFile)
    print(json_parsed)
    #myObject = myFile.read()
    #json_parsed= json.loads(myObject)
    sensor = json_parsed['bandInfo']['sensor']
    print(sensor)
    adiSettings = json_parsed['bandInfo']['adiSettings']
    print(adiSettings)
    hps = json_parsed['hps']
    print(hps)
    i2c = json_parsed['i2c']
    print(i2c)
    bandIndex = json_parsed['bandIndex']
    print(bandIndex)
    timeStamp = json_parsed['bandInfo']['timeStampHealthCheck']
    print(timeStamp)
#preapare header
    healthDataHdlr = open(output_file,'a')
    csvwriter = csv.writer(healthDataHdlr)
    if skip_header:
        print("write to header")
        header = ["escID", "bandIndex", "timeStampHealthCheck"]
        header = header + (sensor.keys())
        header = header + (adiSettings.keys())
        header = header + (hps.keys())
        header = header + (i2c.keys())
        csvwriter.writerow(header)
        skip_header=False
    else:
        print("write values")
        del header[:]
        del values[:]

#prepare values
    values.append(bandIndex)
    values.append(timeStamp)
    for item in sensor.values():
        values.append(item)
    for item in adiSettings.values():
        values.append(item)
    for item in hps.values():
        values.append(item)
    for item in i2c.values():
        values.append(item)
    csvwriter.writerow(values)
    healthDataHdlr.close()
    return

""" Function: Create socket """
def create_socket():
# create a TCP/IP socket
    sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock

if __name__ == '__main__':
    sock = create_socket()
    server_addr = ('localhost', 10000)
    print >>sys.stderr, 'starting up on %s port %s' %server_addr
    while True:
        try:
            sock.connect(server_addr)
            print("Connected.")
            break
        except:
            print >>sys.stderr, "connection error: keep trying"
            time.sleep(2)
            continue
    ts = time.time()
    output_file = output_file + datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + ".csv"
    json_file="/home/sarath/openvpn-monitor/snmp-demo/health_data.json"
    check_file_exists = Path(json_file)
    if check_file_exists.is_file():
        while True:
            sock.recv(1024)
            print("Recv signal: Write to CSV")
            write_to_csv(json_file, output_file)
    else:
        print(output_file)
        print("Json file is not present -- please check if esc_monit is running")
