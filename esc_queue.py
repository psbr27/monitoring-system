#!/usr/bin/env python

from Queue import Queue 
import threading
import mysql.connector
from mysql.connector import MySQLConnection, Error

esc_sn01_Q= Queue()
esc_sn015_Q = Queue()
esc_sn023_Q = Queue()
esc_sn026_Q = Queue()
esc_sn029_Q = Queue()
esc_sn08_Q = Queue()
esc_sn014_Q = Queue()

thread_list=[]

def connect():
    try:
        conn = mysql.connector.connect(host='localhost', database='escdb', user='escmonit', password='passcode')
        if conn.is_connected():
            print('\t\t\t Connected to MySQL database')
            return conn

    except Error as e:
        print(e)

def insert_query_to_hbeat_tbl(sessions, flag):
	conn = connect()
	cursor = conn.cursor()
	sql = "INSERT INTO esc_hbeat_tbl VALUES('%s', '%s', '%d', '%s', '%s', '%s')" % \
					(session['username'], int(session['bytes_sent']), int(session['bytes_recv']), session['local_ip'], session['remote_ip'],session['connected_since'], "UP", 1)
	no_of_rows = cursor.execute(sql)
	conn.commit()
	conn.close()
	cursor.close()



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
def esc_sn014_Q_thread(username):
	thread_list.append(username)
	counter=0
	while True:
		try:
			hb = esc_sn014_Q.get(True, 20)
			if hb:
			    esc_sn014_Q.task_done()
		except:
			print("14:timeout")
			counter = counter + 1
			if counter==3:
				counter=0
				print("\t\t\t\t\tNo heart beat detcted for esc_sn014, raise a trap")
				thread_list.pop(username)
				break
			elif counter < 3:
				continue	

#o==================================o====================================o================================
def esc_sn01_Q_thread(username):
	thread_list.append(username)
	counter=0
	while True:
		try:
			hb = esc_sn01_Q.get(True, 20)
			if hb:
			    esc_sn01_Q.task_done()
		except:
			print("01:timeout")
			counter = counter + 1
			if counter==3:
				counter=0
				print("\t\t\t\t\tNo heart beat detcted for esc_sn01, raise a trap")
				thread_list.pop(username)
				break
			elif counter < 3:
				continue	
#o==================================o====================================o================================
def esc_sn015_Q_thread(username):
	thread_list.append(username)
	counter=0
	while True:
		try:
			hb = esc_sn015_Q.get(True, 20)
			if hb:
			    esc_sn015_Q.task_done()
		except:
			print("15:timeout")
			counter = counter + 1
			if counter==3:
				counter=0
				print("\t\t\t\t\tNo heart beat detcted for esc_sn015, raise a trap")
				thread_list.pop(username)
				break
			elif counter < 3:
				continue	
#o==================================o====================================o================================
def esc_sn023_Q_thread(username):
	thread_list.append(username)
	counter=0
	while True:
		try:
			hb = esc_sn023_Q.get(True, 20)
			if hb:
			    esc_sn023_Q.task_done()
		except:
			print("23:timeout")
			counter = counter + 1
			if counter==3:
				counter=0
				print("\t\t\t\t\tNo heart beat detcted for esc_sn023, raise a trap")
				thread_list.pop(username)
				break
			elif counter < 3:
				continue	
#o==================================o====================================o================================
def esc_sn026_Q_thread(username):
	thread_list.append(username)
	counter=0
	while True:
		try:
			hb = esc_sn026_Q.get(True, 20)
			if hb:
			    esc_sn026_Q.task_done()
		except:
			print("26:timeout")
			counter = counter + 1
			if counter==3:
				counter=0
				print("\t\t\t\t\tNo heart beat detcted for esc_sn026, raise a trap")
				thread_list.pop(username)
				break
			elif counter < 3:
				continue	
#o==================================o====================================o================================
def esc_sn029_Q_thread(username):
	thread_list.append(username)
	counter=0
	while True:
		try:
			hb = esc_sn029_Q.get(True, 20)
			if hb:
			    esc_sn029_Q.task_done()
		except:
			print("29:timeout")
			counter = counter + 1
			if counter==3:
				counter=0
				print("\t\t\t\t\tNo heart beat detcted for esc_sn029, raise a trap")
				thread_list.pop(username)
				break
			elif counter < 3:
				continue	

#o==================================o====================================o================================
def esc_sn08_Q_thread(username):
	thread_list.append(username)
	counter=0
	while True:
		try:
			hb = esc_sn08_Q.get(True, 20)
			if hb:
			    esc_sn08_Q.task_done()
		except:
			print("08:timeout")
			counter = counter + 1
			if counter==3:
				counter=0
				print("\t\t\t\t\tNo heart beat detcted for esc_sn08, raise a trap")
				thread_list.pop(username)
				break
			elif counter < 3:
				continue	

