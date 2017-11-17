#!/usr/bin/python

import pickle
import socket
import sys
import threading
import time

import simplejson as json

import dynamodblib
import logmanager

log_m = logmanager.LogManager()
log = log_m.logger()

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
import esc_queue as esc_q

dyanmo_db = dynamodblib.DynamoDB()
healthDB = dynamodblib.sensorHealthDB()
siteID_list = []
create_flag = 1

cmdGen = cmdgen.CommandGenerator()


# logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

def set_d_b_str(entry, value):
    error_indication, error_status, error_index, var_binds = cmdGen.setCmd(
        cmdgen.CommunityData('federated'),
        cmdgen.UdpTransportTarget(('34.215.95.184', 161)), (entry, rfc1902.OctetString(value)), )
    # Check for errors and print out results
    if error_indication:
        log.error(error_indication)
    else:
        if error_status:
            log.debug('%s at %s' % (error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1] or '?'))
        else:
            for name, val in var_binds:
                log.debug('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


#
def set_d_b_int(entry, value):
    error_indication, error_status, error_index, var_binds = cmdGen.setCmd(
        cmdgen.CommunityData('federated'),
        cmdgen.UdpTransportTarget(('34.215.95.184', 161)), (entry, rfc1902.Integer(value)), )
    # Check for errors and print out results
    if error_indication:
        log.error(error_indication)
    else:
        if error_status:
            log.debug('%s at %s' % (error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1] or '?'))
        else:
            for name, val in var_binds:
                log.debug('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


# unsigned handler
def set_d_b_unsigned(entry, value):
    error_indication, error_status, error_index, var_binds = cmdGen.setCmd(
        cmdgen.CommunityData('federated'),
        cmdgen.UdpTransportTarget(('34.215.95.184', 161)), (entry, rfc1902.Counter64(value)), )
    # Check for errors and print out results
    if error_indication:
        log.error(error_indication)
    else:
        if error_status:
            log.debug('%s at %s' % (error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1] or '?'))
        else:
            for name, val in var_binds:
                log.debug('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


# snmpset -v2c -c federated 34.215.95.184 1.3.6.1.4.1.8072.2.7.1.1.4.1.2.1 s "FL033C"
# esIndex         escID channelId detectionFlag timeStampSensorResults maxRssiDbm minRssiDbm maxSnrDb minSnrDb numDetections numAttempts numDetectionsTimeWindow numAttemptsTimeWindow probDetection probDetectionTimeWindow
stats = "1.3.6.1.4.1.8072.2.7.1.1.3.1."
operational = "1.3.6.1.4.1.8072.2.7.1.1.1.1."

""" Function: Operation state """


def snmp_set_operations(escId, opState, siteId, entry, adminState):
    set_d_b_int((operational + str(1) + "." + str(entry)), escId)
    set_d_b_str((operational + str(2) + "." + str(entry)), siteId)
    set_d_b_str((operational + str(3) + "." + str(entry)), opState)
    set_d_b_str((operational + str(4) + "." + str(entry)), adminState)


""" Function: Thread_2 handle csv file handler requests """


def csv_client_handler(connection, e, t):
    while True:
        while not e.isSet():
            log.debug('wait for event timeout')
            event_is_set = e.wait()
            if event_is_set:
                log.info("Sync sent to CSV app")
                data = connection.send("Sync")
            else:
                log.debug('do nothing')
        time.sleep(2)


""" Function: Thread_1 handle rest server requests """


def snmp_handler_response(new_sock, e):
    global create_flag
    index_counter = 0
    while True:
        data = new_sock.recv(2048)
        if data:
            json_parse = json.loads(data)
            json_file = open("health_data.json", 'w')
            pickle.dump(json_parse, json_file)
            json_file.close()
            log.debug('Event is set')
            # e.set()

            log.info(json_parse)
            band_id = json_parse['bandIndex']
            entry = band_id
            esc_id = json_parse['sensorId']
            # retrieve sensor Id fed_esc_029 to esc_sn029
            log.info("Push data into queue %s" % esc_id)
            esc_q.put_data_into_queue(esc_id, json_parse)

            if (band_id == 0 or band_id == 1) and index_counter < 6:
                log.debug("---> Window Stared <---")
                if create_flag == 1:
                    for num in xrange(1, 7):
                        siteId = esc_id + "_" + str(num)
                        siteID_list.append(siteId)
                        healthDB.createItem(siteId)
                    create_flag = 0
                else:
                    print("")

            if index_counter == 6:
                log.debug("reset counter to zero")
                index_counter = 0

            band_info = json_parse['bandInfo']['timeStampHealthCheck']
            sensor = json_parse['bandInfo']['sensor']
            adi_settings = json_parse['bandInfo']['adiSettings']
            hps = json_parse['hps']
            i2c = json_parse['i2c']

            set_d_b_str((stats + str(2) + "." + str(entry)), esc_id)
            set_d_b_int((stats + str(3) + "." + str(entry)), band_id)
            set_d_b_int((stats + str(4) + "." + str(entry)), band_info)
            set_d_b_int((stats + str(5) + "." + str(entry)), sensor['agcGain'])
            set_d_b_int((stats + str(6) + "." + str(entry)), sensor['gpioOverLoad'])
            set_d_b_int((stats + str(7) + "." + str(entry)), sensor['gpioSPIvalue'])
            set_d_b_str((stats + str(8) + "." + str(entry)), sensor['rmsAverage'])
            set_d_b_int((stats + str(9) + "." + str(entry)), sensor['agcMaxVal'])
            set_d_b_str((stats + str(10) + "." + str(entry)), sensor['noiseRssiDbm'])
            set_d_b_int((stats + str(11) + "." + str(entry)), sensor['dcI'])
            set_d_b_int((stats + str(12) + "." + str(entry)), sensor['dcQ'])
            set_d_b_int((stats + str(13) + "." + str(entry)), sensor['iqImbalanceGaindB'])
            set_d_b_int((stats + str(14) + "." + str(entry)), sensor['iqImbalancePhaseDeg'])
            set_d_b_int((stats + str(15) + "." + str(entry)), sensor['numDmaOverflows'])
            set_d_b_unsigned((stats + str(16) + "." + str(entry)), adi_settings['adiRxLoHz'])
            set_d_b_unsigned((stats + str(17) + "." + str(entry)), adi_settings['adiTxLoHz'])
            set_d_b_int((stats + str(18) + "." + str(entry)), adi_settings['adiGainValue'])
            set_d_b_int((stats + str(19) + "." + str(entry)), adi_settings['adiTxAttenutation'])
            set_d_b_unsigned((stats + str(20) + "." + str(entry)), adi_settings['adiRxClockHz'])
            set_d_b_unsigned((stats + str(21) + "." + str(entry)), adi_settings['adiTxClockHz'])
            set_d_b_int((stats + str(22) + "." + str(entry)), hps['oneMinLoad'])
            set_d_b_int((stats + str(23) + "." + str(entry)), hps['memoryFreeKb'])
            set_d_b_int((stats + str(24) + "." + str(entry)), hps['memoryTotalKb'])
            set_d_b_int((stats + str(25) + "." + str(entry)), hps['upTime'])
            set_d_b_int((stats + str(26) + "." + str(entry)), hps['cpuClockSpeed'])
            set_d_b_str((stats + str(27) + "." + str(entry)), i2c['humidity'])
            set_d_b_str((stats + str(28) + "." + str(entry)), i2c['temperature'])
            set_d_b_int((stats + str(29) + "." + str(entry)), i2c['compass_x_axis'])
            set_d_b_int((stats + str(30) + "." + str(entry)), i2c['compass_y_axis'])
            set_d_b_int((stats + str(31) + "." + str(entry)), i2c['compass_z_axis'])
            set_d_b_int((stats + str(32) + "." + str(entry)), i2c['compassChange'])
            # set the signal to false
            # e.clear()
            # snmpA.trigger_trap()
            # if(i2c['temperature'] > 110):
            #    snmpA.trigger_trap(str(i2c['temperature']))
            healthDB.setItem(siteID_list[index_counter], band_id, str(band_info), sensor['agcGain'], sensor['gpioOverLoad'],
                             sensor['gpioSPIvalue'], str(sensor['rmsAverage']), sensor['agcMaxVal'],
                             str(sensor['noiseRssiDbm']), sensor['dcI'], sensor['dcQ'], sensor['iqImbalanceGaindB'],
                             sensor['iqImbalancePhaseDeg'], sensor['numDmaOverflows'], adi_settings['adiRxLoHz'],
                             adi_settings['adiTxLoHz'], adi_settings['adiGainValue'], adi_settings['adiTxAttenutation'],
                             adi_settings['adiRxClockHz'], adi_settings['adiTxClockHz'], hps['oneMinLoad'],
                             hps['memoryFreeKb'], hps['memoryTotalKb'], hps['upTime'], hps['cpuClockSpeed'],
                             str(i2c['humidity']), str(i2c['temperature']), i2c['compass_x_axis'], i2c['compass_y_axis'],
                             i2c['compass_z_axis'], i2c['compassChange'])
            index_counter = index_counter + 1


def create_socket():
    # create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where esc monitor is listening
    server_addr = ('localhost', 10000)
    log.debug('starting up on %s port %s' % server_addr)
    sock.bind(server_addr)
    return sock


def snmp_stat_handler():
    log.info("Snmp stat handler")
    e = threading.Event()
    sock = create_socket()
    # listen for incoming connections
    sock.listen(2)
    while True:
        log.info('Waiting for a connection..')
        connection, client_address = sock.accept()
        log.info(connection)
        try:
            t4 = threading.Thread(name='rest_receiver', target=snmp_handler_response, args=(connection, e))
            t4.daemon = True
            t4.start()
        except KeyboardInterrupt as msg:
            sock.close()
            sys.exit(0)
