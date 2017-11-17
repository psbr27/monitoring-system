#!/usr/bin/env python

import subprocess

import mysql.connector
from mysql.connector import Error

import esc_queue as esc_q
import logmanager
import portmanagerlib

port_manager = portmanagerlib.PortManager()
log_m = logmanager.LogManager()
log = log_m.logger()

HOST_IP = '34.215.95.184'
count = 0


# connect to MySql server
def connect():
    try:
        conn = mysql.connector.connect(host=HOST_IP, database='escdb', user='escmonit', password='passcode')
        if conn.is_connected():
            return conn

    except Error as e:
        print(e)


# MySQL update query esc_tbl;
def mysql_query_update_esc_tbl(status, count, esc_name):
    conn = connect()
    cursor = conn.cursor()
    sql = "UPDATE esc_tbl SET CommStatus='%s', HeartBeatCount=%d WHERE esc_name='%s'" % (status, count, esc_name)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    cursor.close()


# MySQL select query to fetch esc vip and do ping
def mysql_query_select_esc_tbl_with_ping():
    global count

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM esc_tbl")
    row = cursor.fetchone()
    while row is not None:
        # [u'esc_sn01', 36149, 39122, u'100.61.0.26', u'174.228.132.14', datetime.datetime(2017, 11, 8, 19, 35, 24), u'UP',
        # u'6']
        address = (list(row)[3])
        res = subprocess.call(['ping', '-c', '1', address])
        if res == 0:
            log.debug("Comm is up %s" % address)
        else:
            log.error("No response from %s" % address)
            count = count + 1
            mysql_query_update_esc_tbl("DOWN", count, list(row)[0])

        row = cursor.fetchone()

    cursor.close()
    conn.close()


# MySql select query to fetch the esc table information
def mysql_query_select_esc_tbl():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM esc_tbl")
    row = cursor.fetchone()
    while row is not None:
        row = cursor.fetchone()
    row_count = cursor.rowcount
    cursor.close()
    conn.close()

    return row_count


# MySQL select query the esc deploy table to return port number
def mysql_query_port_no(esc_name):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT * from ESC_DEPLOY_INFO WHERE escName='%s'" % esc_name
    cursor.execute(query)
    row = cursor.fetchone()
    # decode the row and assign ssh port
    # [8, u'esc_sn015', u'FL005', 1, 72900015, 10000]
    ssh_port = (list(row)[5])
    if ssh_port == 0:
        # assign SSH port number
        ssh_port = port_manager.getNextAvailablePort()
    else:
        ssh_port = port_manager.getNextAvailablePort()

    sql = "UPDATE ESC_DEPLOY_INFO SET sshPort=%d WHERE escName='%s'" % (ssh_port, esc_name)
    cursor.execute(sql)
    conn.commit()

    conn.close()
    cursor.close()
    return ssh_port


# MySQL query to update the esc table
def mysql_update_query(sessions, hbeat_count):
    conn = connect()
    cursor = conn.cursor()
    for item in sessions:
        session = sessions[item]
        if session is None:
            continue
        sql = "UPDATE esc_tbl SET TxBytes=%d, RxBytes=%d, lastConnection='%s', HeartBeatCount=%d WHERE esc_name='%s'" % (
            int(session['bytes_sent']), int(session['bytes_recv']), session['connected_since'], hbeat_count,
            session['username'])
        cursor.execute(sql)
        conn.commit()
    conn.close()
    cursor.close()


# MySQL insert esc table
def mysql_insert_query(sessions, flag):
    conn = connect()
    cursor = conn.cursor()
    for item in sessions:
        session = sessions[item]
        if flag:
            esc_q.esc_thread_handler(session['username'])
        sql = "INSERT INTO esc_tbl VALUES('%s', '%d', '%d', '%s', '%s', '%s', '%s', '%d')" % (
            session['username'], int(session['bytes_sent']), int(session['bytes_recv']), session['local_ip'],
            session['remote_ip'], session['connected_since'], "UP", 1)
        cursor.execute(sql)
        conn.commit()
    conn.close()
    cursor.close()


# MySQL update status in deploy table
def mysql_update_deploy_status(status, esc_i_d):
    conn = connect()
    cursor = conn.cursor()
    sql = "UPDATE ESC_DEPLOY_INFO SET deployStatus=%d WHERE esc_name='%s'" % (status, esc_i_d)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    cursor.close()


# MySQL query to fetch the siteId and Label no from Deploy table
def mysql_select_deploy_list(esc_name):
    deploy_list = []

    conn = connect()
    cursor = conn.cursor()
    sql = "SELECT * FROM ESC_DEPLOY_INFO WHERE escName LIKE '%s'" % (esc_name)
    cursor.execute(sql)
    row = cursor.fetchone()
    while row is not None:
        deploy_list.append(list(row)[2])
        deploy_list.append(list(row)[4])
        break
    cursor.close()
    conn.close()

    log.debug(deploy_list)
    return deploy_list


# MySQL get deploy status
def mysql_get_deploy_status(esc_i_d):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT * from ESC_DEPLOY_INFO WHERE escName='%s'" % (esc_i_d)
    cursor.execute(query)
    row = cursor.fetchone()
    # [8, u'esc_sn015', u'FL005', 1, 72900015, 10000]
    deploy_status = (list(row)[3])
    conn.close()
    cursor.close()
    return deploy_status
