#!/usr/bin/env python

from Queue import queue

esc_sn01_Q= Queue()
esc_sn015_Q = Queue()
esc_sn023_Q = Queue()
esc_sn026_Q = Queue()
esc_sn029_Q = Queue()
esc_sn08_Q = Queue()
esc_sn014_Q = Queue()

thread_list=[]

def esc_sn014_Q_thread(username):
    thread_list.append(username)
    while True:
        hb = esc_sn014_Q.get(true, 20)
        if hb:
            esc_sn014_Q.task_done()
        else:
            print("No heart beat detcted for esc_sn014, raise a trap")
            thread_list.pop(username)
            break



def esc_sn029_Q_thread(username):
    thread_list.append(username)
    while True:
        hb = esc_sn029_Q.get(true, 20)
        if hb:
            esc_sn029_Q.task_done()
        else:
            print("No heart beat detcted for esc_sn029, raise a trap")
            thread_list.pop(username)
            break

def esc_sn026_Q_thread(username):
    thread_list.append(username)
    while True:
        hb = esc_sn026_Q.get(true, 20)
        if hb:
            esc_sn026_Q.task_done()
        else:
            print("No heart beat detcted for esc_sn026, raise a trap")
            thread_list.pop(username)
            break

def esc_sn023_Q_thread(username):
    thread_list.append(username)
    while True:
        hb = esc_sn023_Q.get(true, 20)
        if hb:
            esc_sn023_Q.task_done()
        else:
            print("No heart beat detcted for esc_sn023, raise a trap")
            thread_list.pop(username)
            break

def esc_sn015_Q_thread(username):
    thread_list.append(username)
    while True:
        hb = esc_sn015_Q.get(true, 20)
        if hb:
            esc_sn015_Q.task_done()
        else:
            print("No heart beat detcted for esc_sn015, raise a trap")
            thread_list.pop(username)
            break

def esc_sn01_Q_thread(username):
    thread_list.append(username)
    while True:
        hb = esc_sn01_Q.get(true, 20)
        if hb:
            esc_sn01_Q.task_done()
        else:
            print("No heart beat detcted for esc_sn01, raise a trap")
            thread_list.pop(username)
            break

def esc_sn08_Q_thread(username):
    thread_list.append(username)
    while True:
        hb = esc_sn08_Q.get(true, 20)
        if hb:
            esc_sn08_Q.task_done()
        else:
            print("No heart beat detcted for esc_sn08, raise a trap")
            thread_list.pop(username)
            break

