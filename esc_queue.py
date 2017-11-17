#!/usr/bin/env python

import Queue
import threading
import time

import logmanager
import snmp_stat as snmp
import trap_v2c as snmp_trap

log_m = logmanager.LogManager()
log = log_m.logger()
heart_beat_counter = 0
count = 0
heart_beat_dict = {'esc_sn01':0,'esc_sn015':0,'esc_sn023':0,'esc_sn026':0,'esc_sn029':0,'esc_sn08':0,'esc_sn014':0}

esc_sn01_Q = Queue.Queue(100)
esc_sn015_Q = Queue.Queue(100)
esc_sn023_Q = Queue.Queue(100)
esc_sn026_Q = Queue.Queue(100)
esc_sn029_Q = Queue.Queue(100)
esc_sn08_Q = Queue.Queue(100)
esc_sn014_Q = Queue.Queue(100)

thread_list = []


# sensor id is different because it is coming from ESC, where as
# other id is from openvpn
def put_data_into_queue(username, data):
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
        log.info("data available Queue29 \n")
    if username == 'fed_esc_08':
        esc_sn08_Q.put(data)
    if username == 'fed_esc_014':
        esc_sn014_Q.put(data)


# o==================================o====================================o================================
def esc_thread_handler(username):
    if username == 'esc_sn014':
        esc_worker = threading.Thread(name=username, target=esc_sn014__q_thread, args=(username,))
        esc_worker.setDaemon = True
        esc_worker.start()
    if username == 'esc_sn029':
        esc_worker = threading.Thread(name=username, target=esc_sn029__q_thread, args=(username,))
        esc_worker.setDaemon = True
        esc_worker.start()
    if username == 'esc_sn026':
        esc_worker = threading.Thread(name=username, target=esc_sn026__q_thread, args=(username,))
        esc_worker.setDaemon = True
        esc_worker.start()
    if username == 'esc_sn023':
        esc_worker = threading.Thread(name=username, target=esc_sn023__q_thread, args=(username,))
        esc_worker.setDaemon = True
        esc_worker.start()
    if username == 'esc_sn015':
        esc_worker = threading.Thread(name=username, target=esc_sn015__q_thread, args=(username,))
        esc_worker.setDaemon = True
        esc_worker.start()
    if username == 'esc_sn01':
        esc_worker = threading.Thread(name=username, target=esc_sn01__q_thread, args=(username,))
        esc_worker.setDaemon = True
        esc_worker.start()
    if username == 'esc_sn08':
        esc_worker = threading.Thread(name=username, target=esc_sn08__q_thread, args=(username,))
        esc_worker.setDaemon = True
        esc_worker.start()


# o==================================o====================================o================================
# ESC SN 029
# o==================================o====================================o================================
def esc_sn029_handler(username):
    log.debug("Timer invoked esc_sn029_handler every 15sec")
    if esc_sn029_Q.empty():
        heart_beat_counter = heart_beat_dict[username]
        if heart_beat_counter == 3:
            log.warn("No heart beat detcted for esc_sn029, raise a trap")
            #insert_query_to_hbeat_tbl(username, "DOWN", count, "IN-ACTIVE", "DISABLE", 1)
            snmp.snmp_set_operations(29, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
            snmp_trap.trigger_trap("No heartbeat detected")
            heart_beat_dict[username] = 0
        else:
            heart_beat_counter = heart_beat_counter + 1
            heart_beat_dict[username] = heart_beat_counter
    else:
        log.debug('Fetch data from esc_sn029_Q')
        esc_sn029_Q.get(True, 15)
        #insert_query_to_hbeat_tbl(username, "UP", count, "ACTIVE", "ENABLE", 1)
        snmp.snmp_set_operations(29, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        esc_sn029_Q.task_done()

def esc_sn029__q_thread(username):
    log.debug("Created esc_sn029__q_thread")
    thread_list[username] = ""
    while True:
        t = threading.Timer(15.0, esc_sn029_handler, args=(username,))
        log.debug("Starting esc_sn029__q_thread timer")
        t.start() #after 15 seconds, trigger esc_sn029_handler
        time.sleep(15)

# o==================================o====================================o================================
# ESC SN 026
# o==================================o====================================o================================
def esc_sn026_handler(username):
    log.debug("Timer invoked esc_sn026_handler every 15sec")
    if esc_sn026_Q.empty():
        heart_beat_counter = heart_beat_dict[username]
        if heart_beat_counter == 3:
            log.warn("No heart beat detcted for esc_sn026, raise a trap")
            #insert_query_to_hbeat_tbl(username, "DOWN", count, "IN-ACTIVE", "DISABLE", 1)
            snmp.snmp_set_operations(26, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
            snmp_trap.trigger_trap("No heartbeat detected")
            heart_beat_dict[username] = 0
        else:
            heart_beat_counter = heart_beat_counter + 1
            heart_beat_dict[username] = heart_beat_counter
    else:
        log.debug('Fetch data from esc_sn026_Q')
        esc_sn026_Q.get(True, 15)
        #insert_query_to_hbeat_tbl(username, "UP", count, "ACTIVE", "ENABLE", 1)
        snmp.snmp_set_operations(26, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        esc_sn026_Q.task_done()

def esc_sn026__q_thread(username):
    log.debug("Created esc_sn026__q_thread")
    thread_list.append(username)
    while True:
        t2 = threading.Timer(15.0, esc_sn026_handler, args=(username,))
        t2.setName("esc_sn026__q_thread")
        t2.start() #after 15 seconds, trigger esc_sn029_handler
        time.sleep(15)

# o==================================o====================================o================================
# ESC SN 023
# o==================================o====================================o================================
def esc_sn023_handler(username):
    log.debug("Timer invoked esc_sn023_handler every 15sec")
    if esc_sn023_Q.empty():
        heart_beat_counter = heart_beat_dict[username]
        if heart_beat_counter == 3:
            log.warn("No heart beat detcted for esc_sn023, raise a trap")
            #insert_query_to_hbeat_tbl(username, "DOWN", count, "IN-ACTIVE", "DISABLE", 1)
            snmp.snmp_set_operations(23, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
            snmp_trap.trigger_trap("No heartbeat detected")
            heart_beat_dict[username] = 0
        else:
            heart_beat_counter = heart_beat_counter + 1
            heart_beat_dict[username] = heart_beat_counter
    else:
        log.debug('Fetch data from esc_sn023_Q')
        esc_sn023_Q.get(True, 15)
        #insert_query_to_hbeat_tbl(username, "UP", count, "ACTIVE", "ENABLE", 1)
        snmp.snmp_set_operations(23, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        esc_sn023_Q.task_done()

#
def esc_sn023__q_thread(username):
    log.debug("Created esc_sn023__q_thread")
    thread_list.append(username)
    while True:
        t2 = threading.Timer(15.0, esc_sn023_handler, args=(username,))
        t2.setName("esc_sn023__q_thread")
        t2.start() #after 15 seconds, trigger esc_sn023_handler
        time.sleep(15)

# o==================================o====================================o================================
# ESC SN 015
# o==================================o====================================o================================
def esc_sn015_handler(username):
    log.debug("Timer invoked esc_sn015_handler every 15sec")
    if esc_sn015_Q.empty():
        heart_beat_counter = heart_beat_dict[username]
        if heart_beat_counter == 3:
            log.warn("No heart beat detcted for esc_sn015, raise a trap")
            #insert_query_to_hbeat_tbl(username, "DOWN", count, "IN-ACTIVE", "DISABLE", 1)
            snmp.snmp_set_operations(15, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
            snmp_trap.trigger_trap("No heartbeat detected")
            heart_beat_dict[username] = 0
        else:
            heart_beat_counter = heart_beat_counter + 1
            heart_beat_dict[username] = heart_beat_counter
    else:
        log.debug('Fetch data from esc_sn015_Q')
        esc_sn015_Q.get(True, 15)
        #insert_query_to_hbeat_tbl(username, "UP", count, "ACTIVE", "ENABLE", 1)
        snmp.snmp_set_operations(15, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        esc_sn015_Q.task_done()

#
def esc_sn015__q_thread(username):
    log.debug("Created esc_sn015__q_thread")
    thread_list.append(username)
    while True:
        t2 = threading.Timer(15.0, esc_sn015_handler, args=(username,))
        t2.setName("esc_sn015__q_thread")
        t2.start() #after 15 seconds, trigger esc_sn015_handler
        time.sleep(15)


# o==================================o====================================o================================
# ESC SN 014
# o==================================o====================================o================================
def esc_sn014_handler(username):
    log.debug("Timer invoked esc_sn014_handler every 15sec")
    if esc_sn014_Q.empty():
        heart_beat_counter = heart_beat_dict[username]
        if heart_beat_counter == 3:
            log.warn("No heart beat detcted for esc_sn014, raise a trap")
            #insert_query_to_hbeat_tbl(username, "DOWN", count, "IN-ACTIVE", "DISABLE", 1)
            snmp.snmp_set_operations(14, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
            snmp_trap.trigger_trap("No heartbeat detected")
            heart_beat_dict[username] = 0
        else:
            heart_beat_counter = heart_beat_counter + 1
            heart_beat_dict[username] = heart_beat_counter
    else:
        log.debug('Fetch data from esc_sn015_Q')
        esc_sn014_Q.get(True, 15)
        #insert_query_to_hbeat_tbl(username, "UP", count, "ACTIVE", "ENABLE", 1)
        snmp.snmp_set_operations(14, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        esc_sn014_Q.task_done()

#
def esc_sn014__q_thread(username):
    log.debug("Created esc_sn014__q_thread")
    thread_list.append(username)
    while True:
        t2 = threading.Timer(15.0, esc_sn014_handler, args=(username,))
        t2.setName("esc_sn014__q_thread")
        t2.start() #after 15 seconds, trigger esc_sn014_handler
        time.sleep(15)



# o==================================o====================================o================================
# ESC SN 08
# o==================================o====================================o================================
def esc_sn08_handler(username):
    log.debug("Timer invoked esc_sn08_handler every 15sec")
    if esc_sn08_Q.empty():
        heart_beat_counter = heart_beat_dict[username]
        if heart_beat_counter == 3:
            log.warn("No heart beat detcted for esc_sn08, raise a trap")
            #insert_query_to_hbeat_tbl(username, "DOWN", count, "IN-ACTIVE", "DISABLE", 1)
            snmp.snmp_set_operations(8, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
            snmp_trap.trigger_trap("No heartbeat detected")
            heart_beat_dict[username] = 0
        else:
            heart_beat_counter = heart_beat_counter + 1
            heart_beat_dict[username] = heart_beat_counter
    else:
        log.debug('Fetch data from esc_sn08_Q')
        esc_sn08_Q.get(True, 15)
        #insert_query_to_hbeat_tbl(username, "UP", count, "ACTIVE", "ENABLE", 1)
        snmp.snmp_set_operations(8, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        esc_sn08_Q.task_done()

#
def esc_sn08__q_thread(username):
    log.debug("Created esc_sn08__q_thread")
    thread_list.append(username)
    while True:
        t2 = threading.Timer(15.0, esc_sn08_handler, args=(username,))
        t2.setName("esc_sn08__q_thread")
        t2.start() #after 15 seconds, trigger esc_sn08_handler
        time.sleep(15)


# o==================================o====================================o================================
# ESC SN 01
# o==================================o====================================o================================
def esc_sn01_handler(username):
    log.debug("Timer invoked esc_sn01_handler every 15sec")
    if esc_sn01_Q.empty():
        heart_beat_counter = heart_beat_dict[username]
        if heart_beat_counter == 3:
            log.warn("No heart beat detcted for esc_sn01, raise a trap")
            #insert_query_to_hbeat_tbl(username, "DOWN", count, "IN-ACTIVE", "DISABLE", 1)
            snmp.snmp_set_operations(1, "IN-ACTIVE", "ARLINGTON", 1, "DISABLE")
            snmp_trap.trigger_trap("No heartbeat detected")
            heart_beat_dict[username] = 0
        else:
            heart_beat_counter = heart_beat_counter + 1
            heart_beat_dict[username] = heart_beat_counter
    else:
        log.debug('Fetch data from esc_sn01_Q')
        esc_sn01_Q.get(True, 15)
        #insert_query_to_hbeat_tbl(username, "UP", count, "ACTIVE", "ENABLE", 1)
        snmp.snmp_set_operations(1, "ACTIVE", "ARLINGTON", 1, "ENABLE")
        esc_sn01_Q.task_done()

#
def esc_sn01__q_thread(username):
    log.debug("Created esc_sn01__q_thread")
    thread_list.append(username)
    while True:
        t2 = threading.Timer(15.0, esc_sn01_handler, args=(username,))
        t2.setName("esc_sn01__q_thread")
        t2.start() #after 15 seconds, trigger esc_sn01_handler
        time.sleep(15)


