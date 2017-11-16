#!/usr/bin/env python

import Queue
import threading
import mysql.connector
from mysql.connector import MySQLConnection, Error
import time
import trap_v2c as snmpTrap
import snmp_stat as snmpStat


queueLock = threading.Lock()

esc_sn01_Q= Queue.Queue(100)
esc_sn015_Q = Queue.Queue(100)
esc_sn023_Q = Queue.Queue(100)
esc_sn026_Q = Queue.Queue(100)
esc_sn029_Q = Queue.Queue(100)
esc_sn08_Q = Queue.Queue(100)
esc_sn014_Q = Queue.Queue(100)

thread_list=[]

def connect():
    try:
        conn = mysql.connector.connect(host='34.215.95.184', database='escdb', user='escmonit', password='passcode')
        if conn.is_connected():
            print('\t\t\t Connected to MySQL database')
            return conn

    except Error as e:
        print(e)

def insert_query_to_hbeat_tbl(esc_name, heart_beat, hb_count, opState, adminState, flag):
    if flag == 1:
        conn = connect()
        cursor = conn.cursor()
        datecmd = time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO esc_hbeat_tbl VALUES('%s', '%s', '%d', '%s', '%s', '%s')" % \
                        (esc_name, heart_beat, hb_count, opState, adminState, datecmd)
        no_of_rows = cursor.execute(sql)
        conn.commit()
        conn.close()
        cursor.close()

def put_data_into_queue(username,data):
	if username == 'fed_esc_01':
		esc_sn01_Q.put(data)
	if username == 'fed_esc_015':
		esc_sn015_Q.put(data)
	if username == 'fed_esc_023':
		esc_sn023_Q.put(data)
	if username == 'fed_esc_026':
		esc_sn026_Q.put(data)
	if username == 'fed_esc_029':
		esc_sn029_Q.put(data)
        print("\t\t\t\t data available Queue29 \n")
	if username == 'fed_esc_08':
		esc_sn08_Q.put(data)
	if username == 'fed_esc_014':
		esc_sn014_Q.put(data)


#o==================================o====================================o================================
def esc_thread_handler(username):
	if username == 'esc_sn014':
		esc_worker = threading.Thread(name=username, target=esc_sn014_Q_thread, args=(username,))
		esc_worker.setDaemon = True
		esc_worker.start()
	if username == 'esc_sn029':
		esc_worker = threading.Thread(name=username, target=esc_sn029_Q_thread, args=(username,))
		esc_worker.setDaemon = True
		esc_worker.start()
	if username == 'esc_sn026':
		esc_worker = threading.Thread(name=username, target=esc_sn026_Q_thread, args=(username,))
		esc_worker.setDaemon = True
		esc_worker.start()
	if username == 'esc_sn023':
		esc_worker = threading.Thread(name=username, target=esc_sn023_Q_thread, args=(username,))
		esc_worker.setDaemon = True
		esc_worker.start()
	if username == 'esc_sn015':
		esc_worker = threading.Thread(name=username, target=esc_sn015_Q_thread, args=(username,))
		esc_worker.setDaemon = True
		esc_worker.start()
	if username == 'esc_sn01':
		esc_worker = threading.Thread(name=username, target=esc_sn01_Q_thread, args=(username,))
		esc_worker.setDaemon = True
		esc_worker.start()
	if username == 'esc_sn08':
		esc_worker = threading.Thread(name=username, target=esc_sn08_Q_thread, args=(username,))
		esc_worker.setDaemon = True
		esc_worker.start()

#o==================================o====================================o================================
def esc_sn029_Q_thread(username):
    thread_list.append(username)
    counter=0
    count = 0
    while True:
        try:
            hb = esc_sn029_Q.get(True, 15)
            count = count + 1
            print '\t\t\tFetch data from esc_sn029_Q \n'
            esc_sn029_Q.task_done()
            insert_query_to_hbeat_tbl(username,"UP",count,"ACTIVE","ENABLE", count)
            snmpStat.snmp_set_operations(29, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        except Queue.Empty:
            if counter == 3:
                insert_query_to_hbeat_tbl(username,"DOWN",count,"IN-ACTIVE","DISABLE", count)
                print("\t\t\t\t\tNo heart beat detcted for esc_sn029, raise a trap")
                snmpStat.snmp_set_operations(29, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
                snmpTrap.trigger_trap("Operational Down")
                thread_list.remove(username)
                counter = 0
                thread_list.append(username)
            else:
                time.sleep(15)
                counter = counter + 1
#o==================================o====================================o================================
def esc_sn026_Q_thread(username):
    thread_list.append(username)
    counter=0
    count = 0
    while True:
        try:
            hb = esc_sn026_Q.get(True, 15)
            count = count + 1
            print '\t\t\tFetch data from esc_sn026_Q \n'
            esc_sn026_Q.task_done()
            insert_query_to_hbeat_tbl(username,"UP",count,"ACTIVE","ENABLE", count)
        except Queue.Empty:
            if counter == 3:
                insert_query_to_hbeat_tbl(username,"DOWN",count,"IN-ACTIVE","DISABLE", count)
                print("\t\t\t\t\tNo heart beat detcted for esc_sn026, raise a trap")
                thread_list.remove(username)
                counter = 0
                thread_list.append(username)
            else:
                time.sleep(15)
                counter = counter + 1
#


#o==================================o====================================o================================
def esc_sn023_Q_thread(username):
    thread_list.append(username)
    counter=0
    count = 0
    while True:
        try:
            hb = esc_sn023_Q.get(True, 15)
            count = count + 1
            print '\t\t\tFetch data from esc_sn023_Q \n'
            esc_sn023_Q.task_done()
            insert_query_to_hbeat_tbl(username,"UP",count,"ACTIVE","ENABLE", count)
        except Queue.Empty:
            if counter == 3:
                insert_query_to_hbeat_tbl(username,"DOWN",count,"IN-ACTIVE","DISABLE", count)
                print("\t\t\t\t\tNo heart beat detcted for esc_sn023, raise a trap")
                thread_list.remove(username)
                counter = 0
                thread_list.append(username)
            else:
                time.sleep(15)
                counter = counter + 1
#

#o==================================o====================================o================================
def esc_sn015_Q_thread(username):
    thread_list.append(username)
    counter=0
    count = 0
    while True:
        try:
            hb = esc_sn015_Q.get(True, 15)
            count = count + 1
            print '\t\t\tFetch data from esc_sn015_Q \n'
            esc_sn015_Q.task_done()
            insert_query_to_hbeat_tbl(username,"UP",count,"ACTIVE","ENABLE", count)
        except Queue.Empty:
            if counter == 3:
                insert_query_to_hbeat_tbl(username,"DOWN",count,"IN-ACTIVE","DISABLE", count)
                print("\t\t\t\t\tNo heart beat detcted for esc_sn015, raise a trap")
                thread_list.remove(username)
                counter = 0
                thread_list.append(username)
            else:
                time.sleep(15)
                counter = counter + 1
#
#o==================================o====================================o================================
def esc_sn014_Q_thread(username):
    thread_list.append(username)
    counter=0
    count = 0
    while True:
        try:
            hb = esc_sn014_Q.get(True, 15)
            count = count + 1
            print '\t\t\tFetch data from esc_sn014_Q \n'
            esc_sn014_Q.task_done()
            insert_query_to_hbeat_tbl(username,"UP",count,"ACTIVE","ENABLE", count)
        except Queue.Empty:
            if counter == 3:
                insert_query_to_hbeat_tbl(username,"DOWN",count,"IN-ACTIVE","DISABLE", count)
                print("\t\t\t\t\tNo heart beat detcted for esc_sn014, raise a trap")
                thread_list.remove(username)
                counter = 0
                thread_list.append(username)
            else:
                time.sleep(15)
                counter = counter + 1
#
#o==================================o====================================o================================
def esc_sn08_Q_thread(username):
    thread_list.append(username)
    counter=0
    count = 0
    while True:
        try:
            hb = esc_sn08_Q.get(True, 15)
            count = count + 1
            print '\t\t\tFetch data from esc_sn08_Q \n'
            esc_sn08_Q.task_done()
            insert_query_to_hbeat_tbl(username,"UP",count,"ACTIVE","ENABLE", count)
        except Queue.Empty:
            if counter == 3:
                insert_query_to_hbeat_tbl(username,"DOWN",count,"IN-ACTIVE","DISABLE", count)
                print("\t\t\t\t\tNo heart beat detcted for esc_sn08, raise a trap")
                thread_list.remove(username)
                counter = 0
                thread_list.append(username)
            else:
                time.sleep(15)
                counter = counter + 1
#
#o==================================o====================================o================================
def esc_sn01_Q_thread(username):
    thread_list.append(username)
    counter=0
    count = 0
    while True:
        try:
            hb = esc_sn01_Q.get(True, 15)
            count = count + 1
            print '\t\t\tFetch data from esc_sn01_Q \n'
            esc_sn01_Q.task_done()
            insert_query_to_hbeat_tbl(username,"UP",count,"ACTIVE","ENABLE", count)
        except Queue.Empty:
            if counter == 3:
                insert_query_to_hbeat_tbl(username,"DOWN",count,"IN-ACTIVE","DISABLE", count)
                print("\t\t\t\t\tNo heart beat detcted for esc_sn01, raise a trap")
                thread_list.remove(username)
                counter = 0
                thread_list.append(username)
            else:
                time.sleep(15)
                counter = counter + 1
#

