#!/usr/bin/env python

import time
import sys
import argparse
import fetch_data_openvpn_mgmt as Mgmt
import config_loader as cfgInst
import Queue
import threading
import snmp_stat as snmpStat
import rest_server as restSrv

import mysql.connector
from mysql.connector import MySQLConnection, Error
interval=15


def process_data():
    while True:
            Mgmt.query_with_fetchnone(True)
            time.sleep(1)


def connect():
    try:
        conn = mysql.connector.connect(host='localhost', database='escdb', user='escmonit', password='passcode')
        if conn.is_connected():
            print('\t\t\t Connected to MySQL database')
            return conn

    except Error as e:
        print(e)


def cleanup_db():
    print("Preparing DELETE >>>")
    conn = connect()
    cursor = conn.cursor()
    sql = "DELETE FROM esc_tbl;"
    no_of_rows = cursor.execute(sql)
    conn.commit()
    conn.close()
    cursor.close()


def main(**kwargs):
    argLen = len(sys.argv)
    print(argLen)
    cfg = cfgInst.ConfigLoader(args.config)
    cleanup_db()
    counter = 0
    tName = "ping_worker"
    threadID = 1
    #start ping manager thread
#create threads
    t1 = threading.Thread(name='ping', target=process_data)
    t1.daemon = True
    t1.start()
#second thread
    t2 = threading.Thread(name='snmp_stat', target=snmpStat.snmp_stat_hdlr)
    t2.daemon = True
    t2.start()
#rest server thread
    t3 = threading.Thread(name='rest_server', target=restSrv.rest_server_hdlr)
    t3.daemon = True
    t3.start()
    while True:
        print(" !!!!!!!!!!!!!!!!!!!!!!!!!! %d !!!!!!!!!!!!!!!!!!!!!!!!!!! " %(counter+1))
        monitor = Mgmt.OpenvpnMgmtInterface(cfg, **kwargs)
        time.sleep(interval)

# ----------------------------------------------------------------

def get_args():
    parser = argparse.ArgumentParser(
        description='Display a html page with openvpn status and connections')
    parser.add_argument('-d', '--debug', action='store_true',
                        required=False, default=False,
                        help='Run in debug mode')
    parser.add_argument('-c', '--config', type=str,
                        required=False, default='./openvpn-monitor.conf',
                        help='Path to config file openvpn-monitor.conf')
    return parser.parse_args()

# ----------------------------------------------------------------


if __name__ == '__main__':
    args = get_args()
    main()
