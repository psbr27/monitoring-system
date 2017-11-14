#!/usr/bin/python

import socket
import sys
import simplejson as json
import trap_v2c as snmpA
import unicodedata
import dynamodblib
import boto3
import atexit
import pickle
import threading
import time
import logging

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
import esc_queue as escQ

dyanmodb = dynamodblib.DynamoDB()
healthDB = dynamodblib.sensorHealthDB()
siteID_list=[]
create_flag=1

cmdGen = cmdgen.CommandGenerator()

#logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

def setDB_str(entry, value):
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
        cmdgen.CommunityData('federated'),
        cmdgen.UdpTransportTarget(('34.215.95.184', 161)),
        (entry, rfc1902.OctetString(value)),
        )
# Check for errors and print out results
    if errorIndication:
            print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                  errorIndex and varBinds[int(errorIndex) - 1] or '?'))
        else:
            for name, val in varBinds:
                print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


def setDB_int(entry, value):
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
        cmdgen.CommunityData('federated'),
        cmdgen.UdpTransportTarget(('34.215.95.184', 161)),
        (entry, rfc1902.Integer(value)),
        )
# Check for errors and print out results
    if errorIndication:
            print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                  errorIndex and varBinds[int(errorIndex) - 1] or '?'))
        else:
            for name, val in varBinds:
                print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


# unsigned handler
def setDB_unsigned(entry, value):
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
        cmdgen.CommunityData('federated'),
        cmdgen.UdpTransportTarget(('34.215.95.184', 161)),
        (entry, rfc1902.Counter64(value)),
        )
# Check for errors and print out results
    if errorIndication:
            print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                  errorIndex and varBinds[int(errorIndex) - 1] or '?'))
        else:
            for name, val in varBinds:
                print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))



# snmpset -v2c -c federated 34.215.95.184 1.3.6.1.4.1.8072.2.7.1.1.4.1.2.1 s "FL033C"
# esIndex         escID channelId detectionFlag timeStampSensorResults maxRssiDbm minRssiDbm maxSnrDb minSnrDb numDetections numAttempts numDetectionsTimeWindow numAttemptsTimeWindow probDetection probDetectionTimeWindow
stats = "1.3.6.1.4.1.8072.2.7.1.1.3.1."


#atexit.register(cleanup)


""" Function: Thread_2 handle csv file ahndler requests """
def csv_client_hdlr(connection,e,t):
    while True:
        while not e.isSet():
            print('wait for event timeout')
            event_is_set = e.wait()
            if event_is_set:
                print("Sync sent to CSV app")
                data=connection.send("Sync")
            else:
                print('do nothing')
        time.sleep(2)


""" Function: Thread_1 handle rest server requests """


def handle_response(data):
    global create_flag
    index_counter = 0
    hb_counter=0
# receive the data in small chunks
    #while True:
    print("(rest_server) Waiting for data...")
    #data = connection.recv(2048)
    if data:
	    json_parse = json.loads(data)
	    jsonHdlr = open("health_data.json", 'w')
	    pickle.dump(json_parse, jsonHdlr)
	    jsonHdlr.close()
	    print('Event is set')
	    #e.set()

	    print(json_parse)
	    bandId = json_parse['bandIndex']

	    entry = bandId
	    escId = json_parse['sensorId'] 
            #retrieve sensor Id fed_esc_029 to esc_sn029
            newEscId = escId[4:7] + "sn" + escId[8:10] +"_Q"
            escQ.newEscId.put(json_parse)


	    print("----------------------- rest_server_hdlr ---------------------\n")
	    if ((bandId == 0 or bandId == 1) and index_counter < 6):
		print("---> Window Stared <---")
		if (create_flag == 1):
		    for num in xrange(1,7):
			siteId = escId + "_" + str(num)
			siteID_list.append(siteId)
			healthDB.createItem(siteId)
		    create_flag = 0
		else:
			print("")

	    if(index_counter == 6):
		print("reset counter to zero")
		index_counter = 0

	    bandInfo = json_parse['bandInfo']['timeStampHealthCheck']
	    sensor = json_parse['bandInfo']['sensor']
	    adiSettings = json_parse['bandInfo']['adiSettings']
	    hps = json_parse['hps']
	    i2c = json_parse['i2c']

	# print("DEBUG -> timeStamp %s" %bandInfo)
	# print("DEBUG -> sensor %s" %sensor)
	# print("DEBUG -> adiSettings %s" %adiSettings)
	# print("DEBUG -> hps%s" %hps)
	# print("DEBUG -> i2c%s" %i2c)

	    setDB_str((stats + str(2) + "." + str(entry)), escId);
	    setDB_int((stats + str(3) + "." + str(entry)), bandId);
	    setDB_int((stats + str(4) + "." + str(entry)), bandInfo);
	    setDB_int((stats + str(5) + "." + str(entry)), sensor['agcGain']);
	    setDB_int((stats + str(6) + "." + str(entry)),
		      sensor['gpioOverLoad']);
	    setDB_int((stats + str(7) + "." + str(entry)),
		      sensor['gpioSPIvalue']);
	    setDB_str((stats + str(8) + "." + str(entry)),
		      sensor['rmsAverage']);
	    setDB_int((stats + str(9) + "." + str(entry)),
		      sensor['agcMaxVal']);
	    setDB_str((stats + str(10) + "." + str(entry)),
		      sensor['noiseRssiDbm']);
	    setDB_int((stats + str(11) + "." + str(entry)), sensor['dcI']);
	    setDB_int((stats + str(12) + "." + str(entry)), sensor['dcQ']);
	    setDB_int((stats + str(13) + "." + str(entry)),
		      sensor['iqImbalanceGaindB']);
	    setDB_int((stats + str(14) + "." + str(entry)),
		      sensor['iqImbalancePhaseDeg']);
	    setDB_int((stats + str(15) + "." + str(entry)),
		      sensor['numDmaOverflows']);
	    setDB_unsigned((stats + str(16) + "." + str(entry)),
			   adiSettings['adiRxLoHz']);
	    setDB_unsigned((stats + str(17) + "." + str(entry)),
			   adiSettings['adiTxLoHz']);
	    setDB_int((stats + str(18) + "." + str(entry)),
		      adiSettings['adiGainValue']);
	    setDB_int((stats + str(19) + "." + str(entry)),
		      adiSettings['adiTxAttenutation']);
	    setDB_unsigned((stats + str(20) + "." + str(entry)),
			   adiSettings['adiRxClockHz']);
	    setDB_unsigned((stats + str(21) + "." + str(entry)),
			   adiSettings['adiTxClockHz']);
	    setDB_int((stats + str(22) + "." + str(entry)), hps['oneMinLoad']);
	    setDB_int((stats + str(23) + "." + str(entry)),
		      hps['memoryFreeKb']);
	    setDB_int((stats + str(24) + "." + str(entry)),
		      hps['memoryTotalKb']);
	    setDB_int((stats + str(25) + "." + str(entry)), hps['upTime']);
	    setDB_int((stats + str(26) + "." + str(entry)),
		      hps['cpuClockSpeed']);
	    setDB_str((stats + str(27) + "." + str(entry)), i2c['humidity']);
	    setDB_str((stats + str(28) + "." + str(entry)),
		      i2c['temperature']);
	    setDB_int((stats + str(29) + "." + str(entry)),
		      i2c['compass_x_axis']);
	    setDB_int((stats + str(30) + "." + str(entry)),
		      i2c['compass_y_axis']);
	    setDB_int((stats + str(31) + "." + str(entry)),
		      i2c['compass_z_axis']);
	    setDB_int((stats + str(32) + "." + str(entry)),
		      i2c['compassChange']);
	#set the signal to false
	    #e.clear()
	    print('Event is set to False')
	# snmpA.trigger_trap()
	    if(i2c['temperature'] > 109):
		snmpA.trigger_trap(str(i2c['temperature']))
	    print(siteID_list)
	    hb_counter = hb_counter + 1
	    healthDB.setItem(siteID_list[index_counter],bandId, str(bandInfo), sensor['agcGain'], sensor['gpioOverLoad'], sensor['gpioSPIvalue'], str(sensor['rmsAverage']), sensor['agcMaxVal'], str(sensor['noiseRssiDbm']), sensor['dcI'], sensor['dcQ'], sensor['iqImbalanceGaindB'], sensor['iqImbalancePhaseDeg'], sensor['numDmaOverflows'], adiSettings['adiRxLoHz'], adiSettings['adiTxLoHz'], adiSettings['adiGainValue'], adiSettings['adiTxAttenutation'], adiSettings['adiRxClockHz'], adiSettings['adiTxClockHz'], hps['oneMinLoad'], hps['memoryFreeKb'], hps['memoryTotalKb'], hps['upTime'], hps['cpuClockSpeed'], str(i2c['humidity']), str(i2c['temperature']), i2c['compass_x_axis'], i2c['compass_y_axis'], i2c['compass_z_axis'], i2c['compassChange'])
	    index_counter = index_counter + 1



def hb_monit_hdlr(e):
#access the sql database to know the count of heartbeat
    while True:
        time.sleep(1)


def create_socket():
# create a TCP/IP socket
    sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# onnect the socket to the port where esc monitor is listening
    server_addr = ('localhost', 10000)
    print >>sys.stderr, 'starting up on %s port %s' %server_addr
    sock.bind(server_addr)
    return sock


def snmp_stat_hdlr():
    print("Snmp stat handler")
    Thread1 = True
    e = threading.Event()
    sock = create_socket()
# listen for incoming connections
    sock.listen(2)
#create hb thread
    t3 = threading.Thread(name='hb_monitor', target=hb_monit_hdlr, args=(e,))
    t3.start()

    while True:
        print('Waiting for a connection..')
        connection, client_addr = sock.accept()
        try:
            print >>sys.stderr, 'connection from', client_addr
            if Thread1:
                #t1 = threading.Thread(name='rest_server', target=rest_server_hdlr, args=(connection, e,))
                #t1.start()
                #start_new_thread(rest_server_hdlr,(connection,))
                Thread1=False
                print(connection)
            else:
                t2 = threading.Thread(name='csv_client', target=csv_client_hdlr, args=(connection, e,2))
                t2.start()
                print(connection)
                #start_new_thread(csv_client_hdlr,(connection,))
        except KeyboardInterrupt as msg:
            sock.close()
            sys.exit(0)


