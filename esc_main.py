#!/usr/bin/env python

import argparse
import sys
import threading
import time

import config_loader as cfg_instance
import fetch_data_openvpn_mgmt as Mgmt
import logmanager
import mysql_queries as mysql
import rest_server as server
import snmp_stat as snmp

interval = 15
log_m = logmanager.LogManager()
log = log_m.logger()


# Ping handler - ping each vpn client connection and
# update the status in Mysql
def ping_handler():
    log.info("Created ping handler thread")
    while True:
        mysql.mysql_query_select_esc_tbl_with_ping()


# Delete MySql data tables before start of the application
def cleanup_db():
    log.debug("Delete esc_tbl and esc_hbeat_tbl from escdb database")
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "DELETE FROM esc_tbl;"
    cursor.execute(sql)
    sql = "DELETE FROM esc_hbeat_tbl;"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    cursor.close()


def main(**kwargs):
    arlen = len(sys.argv)
    cfg = cfg_instance.ConfigLoader(args.config)
    cleanup_db()

    # connection thread : ping
    t1 = threading.Thread(name='ping', target=ping_handler)
    t1.daemon = True
    t1.start()

    # rest server thread
    #t2 = threading.Thread(name='rest_server', target=server.rest_server_handler())
    #t2.daemon = True
    #t2.start()

    # rest server thread
    t3 = threading.Thread(name='mgmt_handler', target=snmp.snmp_stat_handler)
    t3.daemon = True
    t3.start()

    log.info("Created management_handler thread")
    counter = 0
    while True:
        counter = counter + 1
        log.info("=====o=====o=====o=====o=====o===== %d =====o=====o=====o=====o=====o===== " % counter)
        monitor = Mgmt.OpenvpnMgmtInterface(cfg, **kwargs)
        time.sleep(interval)

    t1.join()
    #t2.join()
    #t3.join()
    log.debug("Exiting main thread")


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
