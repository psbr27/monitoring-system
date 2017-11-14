#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

try:
    from ipaddr import IPAddress as ip_address
    from ipaddr import IPv6Address
except ImportError:
    from ipaddress import ip_address, IPv6Address

import subprocess
import socket
import re
import argparse
import GeoIP
import sys
import time, os
import atexit
import iptablelib
import portmanagerlib
from datetime import datetime
from humanize import naturalsize
from collections import OrderedDict, deque
from pprint import pformat
from semantic_version import Version as semver
import mysql.connector
import esc_main as escMain
import esc_queue as escQ
from mysql.connector import MySQLConnection, Error

import boto3
global workQueue

def cleanup():
	global iptablelib
	iptables.deleteIpTable()

iptables = iptablelib.IpTablesLib('100.61.0.1','10.1.1.199')
iptables.installIpTableNorth('10.1.1.77',8000,25000)
portmanager = portmanagerlib.PortManager()
atexit.register(cleanup)
client  = boto3.client('sns')

interval=15


index_dict_buck1={}
index_dict_buck2={}


#__________________________________________________________________________________________________
def get_deploy_status(escID):
	conn = connect()
	cursor = conn.cursor()
	query = "SELECT * from ESC_DEPLOY_INFO WHERE escName='%s'" %(escID)
	cursor.execute(query)
        row = cursor.fetchone()
#[8, u'esc_sn015', u'FL005', 1, 72900015, 10000]
	deployStatus = (list(row)[3])
#decode the row and assign ssh port
	conn.close()
	cursor.close()
	return deployStatus

#__________________________________________________________________________________________________
def verify_if_port_exists(escID):
#fetch the row from ESC_DEPLOY_INFO table;
	conn = connect()
	cursor = conn.cursor()
	query = "SELECT * from ESC_DEPLOY_INFO WHERE escName='%s'" %(escID)
	cursor.execute(query)
        row = cursor.fetchone()
#decode the row and assign ssh port
#[8, u'esc_sn015', u'FL005', 1, 72900015, 10000]
	sshPort = (list(row)[5])
	if sshPort == 0:
#assign SSH port number
                sshPort = portmanager.getNextAvailablePort()
	else:
                sshPort = portmanager.getNextAvailablePort()
	#	query = "SELECT * from ESC_DEPLOY_INFO WHERE sshPort=%d" %(sshPort)
	#	cursor.execute(query)
#		row = cursor.fetchone()
#		while row is not None:
#			print(row)
#			row = cursor.fetchone()
#		count = cursor.rowcount
#		print("---- ssh --- \n")
#		print(count)


#update the table with new port number
	sql = "UPDATE ESC_DEPLOY_INFO SET sshPort=%d WHERE escName='%s'" %(sshPort, escID)
	cursor.execute(sql)
	conn.commit()

	conn.close()
	cursor.close()
	return sshPort
#__________________________________________________________________________________________________

def notify_sms(esc_id, siteID, escLabel):

        pySubject = "Alert: ESC Deployed"
        pyMessage = "ESC deployed successfully at site: " + siteID + "\n" + " ESC Label Number: " +  escLabel + "\n"
        response = client.list_subscriptions_by_topic(
                        TopicArn='arn:aws:sns:us-west-2:796687173965:ESC_Deploy_Notification',
                        NextToken=''
                        )
        print(response)
        response = client.publish(
                        TopicArn='arn:aws:sns:us-west-2:796687173965:ESC_Deploy_Notification',
                        Message= pyMessage,
                        Subject= pySubject,
                        MessageStructure='Raw'
                        )
#
#__________________________________________________________________________________________________

def notify_email(esc_id, siteID, escLabel):

        pySubject = "Alert: ESC Deployed"
        pyMessage = "ESC deployed successfully at site: " + siteID + "\n" + " ESC Label Number: " +  escLabel + "\n"
        response = client.list_subscriptions_by_topic(
                        TopicArn='arn:aws:sns:us-west-2:796687173965:NotifyDeployment',
                        NextToken=''
                        )
        print(response)
        response = client.publish(
                        TopicArn='arn:aws:sns:us-west-2:796687173965:NotifyDeployment',
                        Message= pyMessage,
                        Subject= pySubject,
                        MessageStructure='Raw'
                        )
#
#__________________________________________________________________________________________________
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

#connect to MySQL database
def connect():
    try:
        conn = mysql.connector.connect(host='localhost', database='escdb', user='escmonit', password='passcode')
        if conn.is_connected():
            return conn

    except Error as e:
        print(e)

#__________________________________________________________________________________________________
def update_database(sessions, HbeatCount):
	conn = connect()
	cursor = conn.cursor()
	for item in sessions:
		session = sessions[item]
		if session is None:
			continue
		#sql = "UPDATE esc_tbl SET TxBytes=%d, RxBytes=%d, LocalIp=%s, RemoteIp=%s, lastConnection=%s, CommStatus=%s, HeartBeatCount=%d, WHERE esc_name=%s" % \
		#		(int(session['bytes_sent']), int(session['bytes_recv']), session['local_ip'], session['remote_ip'],session['connected_since'], "UP", 1, session['username'])
		sql = "UPDATE esc_tbl SET TxBytes=%d, RxBytes=%d, lastConnection='%s', HeartBeatCount=%d WHERE esc_name='%s'" %(int(session['bytes_sent']), int(session['bytes_recv']),session['connected_since'],HbeatCount, session['username'])
		cursor.execute(sql)
		conn.commit()
	conn.close()
	cursor.close()



#__________________________________________________________________________________________________
def prepare_insert_query(sessions, flag):
	conn = connect()
	cursor = conn.cursor()
	for item in sessions:
		session = sessions[item]
		if flag:
			escQ.esc_thread_handler(session['username'])
		sql = "INSERT INTO esc_tbl VALUES('%s', '%d', '%d', '%s', '%s', '%s', '%s', '%d')" % \
						(session['username'], int(session['bytes_sent']), int(session['bytes_recv']), session['local_ip'], session['remote_ip'],session['connected_since'], "UP", 1)
		no_of_rows = cursor.execute(sql)
		conn.commit()
	conn.close()
	cursor.close()

#__________________________________________________________________________________________________
def update_comm(commStatus, HbeatCount, escId):
    conn = connect()
    cursor = conn.cursor()
    sql = "UPDATE esc_tbl SET CommStatus='%s', HeartBeatCount=%d WHERE esc_name='%s'" %(commStatus, HbeatCount, escId)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    cursor.close()

def update_deploy_status(status, escID):
    conn = connect()
    cursor = conn.cursor()
    sql = "UPDATE ESC_DEPLOY_INFO SET deployStatus=%d WHERE esc_name='%s'" %(status, escID)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    cursor.close()


#__________________________________________________________________________________________________
#fetch number of rows
def query_with_fetchnone(pingFlag):
    count=0
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM esc_tbl")

        row = cursor.fetchone()

        while row is not None:
#[u'esc_sn01', 36149, 39122, u'100.61.0.26', u'174.228.132.14', datetime.datetime(2017, 11, 8, 19, 35, 24), u'UP', u'6']
            address = (list(row)[3])
            if pingFlag:
                res = subprocess.call(['ping', '-c', '1', address])
                if res == 0:
                    print("Comm is up %s" %(address))
                else:
                    print("No response from %s" %(address))
                    status="DOWN"
#update db if comm is down
                    update_comm(status, 1, list(row)[0])
            row = cursor.fetchone()

        count = cursor.rowcount

        cursor.close()
        conn.close()

    except Error as e:
        print(e)

    return count


def get_siteid_lableno(username):
	deploy_list=[]
	try:
		conn = connect()
		cursor = conn.cursor()
		print(username)
		sql = "SELECT * FROM ESC_DEPLOY_INFO WHERE escName LIKE '%s'" %(username)
		cursor.execute(sql)

		row = cursor.fetchone()
		print(row)
		while row is not None:
			deploy_list.append(list(row)[2])
			deploy_list.append(list(row)[4])
			break
		cursor.close()
		conn.close()
	except Error as e:
		print(e)

	print(deploy_list)
	return deploy_list
#__________________________________________________________________________________________________

def output(s):
    global wsgi, wsgi_output
    if not wsgi:
        print(s)
    else:
        wsgi_output += s


def info(*objs):
    print("INFO:", *objs, file=sys.stderr)


def warning(*objs):
    print("WARNING:", *objs, file=sys.stderr)


def debug(*objs):
    print("DEBUG:\n", *objs, file=sys.stderr)

def get_date(date_string, uts=False):
    if not uts:
        return datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y")
    else:
        return datetime.fromtimestamp(float(date_string))


def get_str(s):
    if sys.version_info[0] == 2 and s is not None:
        return s.decode('ISO-8859-1')
    else:
        return s

#__________________________________________________________________________________________________

class OpenvpnMgmtInterface(object):

    def __init__(self, cfg, **kwargs):
        self.vpns = cfg.vpns

        if 'vpn_id' in kwargs:
            vpn = self.vpns[kwargs['vpn_id']]
            self._socket_connect(vpn)
            if vpn['socket_connected']:
                version = self.send_command('version\n')
                sem_ver = semver(self.parse_version(version).split(' ')[1])
                if sem_ver.minor == 4 and 'port' not in kwargs:
                    command = 'client-kill {0!s}\n'.format(kwargs['client_id'])
                else:
                    command = 'kill {0!s}:{1!s}\n'.format(kwargs['ip'], kwargs['port'])
                info('Sending command: {0!s}'.format(command))
                self.send_command(command)
                self._socket_disconnect()

        geoip_data = cfg.settings['geoip_data']
        self.gi = GeoIP.open(geoip_data, GeoIP.GEOIP_STANDARD)

        for key, vpn in list(self.vpns.items()):
            self._socket_connect(vpn)
            if vpn['socket_connected']:
                self.collect_data(vpn)
                self._socket_disconnect()

    def collect_data(self, vpn):
        version = self.send_command('version\n')
        vpn['version'] = self.parse_version(version)
        vpn['semver'] = semver(vpn['version'].split(' ')[1])
        state = self.send_command('state\n')
        vpn['state'] = self.parse_state(state)
        stats = self.send_command('load-stats\n')
        vpn['stats'] = self.parse_stats(stats)
        status = self.send_command('status 3\n')
        vpn['sessions'] = self.parse_status(status, self.gi, vpn['semver'])
#Sarath -> Sync with DB
        print(index_dict_buck2)
        count = query_with_fetchnone(False)
        len_dict = (len(index_dict_buck2))
#if count is ZERO; then insert query into esc_tbl
        if count is -1:
		prepare_insert_query(vpn['sessions'], True)

        if count == len_dict:
            print("\t\t\t DB is in sync with App")
        elif count > len_dict:
            print("\t\t\t Looks like connections are lost in App.. please sync with Db")
        elif count < len_dict:
            print("\t\t\t new connections in App.. please sync with Db")
	    escMain.cleanup_db()
            prepare_insert_query(vpn['sessions'], False)
	print("HB thread active are...")
	print(escQ.thread_list)

    def _socket_send(self, command):
        if sys.version_info[0] == 2:
            self.s.send(command)
        else:
            self.s.send(bytes(command, 'utf-8'))

    def _socket_recv(self, length):
        if sys.version_info[0] == 2:
            return self.s.recv(length)
        else:
            return self.s.recv(length).decode('utf-8')

    def _socket_connect(self, vpn):
        host = vpn['host']
        port = int(vpn['port'])
        timeout = 3
        self.s = False
        try:
            self.s = socket.create_connection((host, port), timeout)
            if self.s:
                vpn['socket_connected'] = True
                data = ''
                while 1:
                    socket_data = self._socket_recv(1024)
                    data += socket_data
                    if data.endswith('\r\n'):
                        break
        except socket.timeout as e:
            vpn['error'] = '{0!s}'.format(e)
            warning('socket timeout: {0!s}'.format(e))
            vpn['socket_connected'] = False
            if self.s:
                self.s.shutdown(socket.SHUT_RDWR)
                self.s.close()
        except socket.error as e:
            vpn['error'] = '{0!s}'.format(e.strerror)
            warning('socket error: {0!s}'.format(e))
            vpn['socket_connected'] = False
        except Exception as e:
            vpn['error'] = '{0!s}'.format(e)
            warning('unexpected error: {0!s}'.format(e))
            vpn['socket_connected'] = False

    def _socket_disconnect(self):
        self._socket_send('quit\n')
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()

    def send_command(self, command):
        self._socket_send(command)
        data = ''
        if command.startswith('kill') or command.startswith('client-kill'):
            return
        while 1:
            socket_data = self._socket_recv(1024)
            socket_data = re.sub('>INFO(.)*\r\n', '', socket_data)
            data += socket_data
            if command == 'load-stats\n' and data != '':
                break
            elif data.endswith("\nEND\r\n"):
                break
        return data

    @staticmethod
    def parse_state(data):
        state = {}
        for line in data.splitlines():
            parts = line.split(',')
            if parts[0].startswith('>INFO') or \
               parts[0].startswith('END') or \
               parts[0].startswith('>CLIENT'):
                continue
            else:
                state['up_since'] = get_date(date_string=parts[0], uts=True)
                state['connected'] = parts[1]
                state['success'] = parts[2]
                if parts[3]:
                    state['local_ip'] = ip_address(parts[3])
                else:
                    state['local_ip'] = ''
                if parts[4]:
                    state['remote_ip'] = ip_address(parts[4])
                    state['mode'] = 'Client'
                else:
                    state['remote_ip'] = ''
                    state['mode'] = 'Server'
        return state

    @staticmethod
    def parse_stats(data):
        stats = {}
        line = re.sub('SUCCESS: ', '', data)
        parts = line.split(',')
        stats['nclients'] = int(re.sub('nclients=', '', parts[0]))
        stats['bytesin'] = int(re.sub('bytesin=', '', parts[1]))
        stats['bytesout'] = int(re.sub('bytesout=', '', parts[2]).replace('\r\n', ''))
        print(stats)
        return stats

    @staticmethod
    def parse_status(data, gi, version):
        client_section = False
        routes_section = False
        sessions = {}
        client_session = {}
        num = 1

        for line in data.splitlines():
            parts = deque(line.split('\t'))

            if parts[0].startswith('END'):
                break
            if parts[0].startswith('TITLE') or \
               parts[0].startswith('GLOBAL') or \
               parts[0].startswith('TIME'):
                continue
            if parts[0] == 'HEADER':
                if parts[1] == 'CLIENT_LIST':
                    client_section = True
                    routes_section = False
                if parts[1] == 'ROUTING_TABLE':
                    client_section = False
                    routes_section = True
                continue

            if parts[0].startswith('TUN') or \
               parts[0].startswith('TCP') or \
               parts[0].startswith('Auth'):
                parts = parts[0].split(',')
            if parts[0] == 'TUN/TAP read bytes':
                client_session['tuntap_read'] = int(parts[1])
                continue
            if parts[0] == 'TUN/TAP write bytes':
                client_session['tuntap_write'] = int(parts[1])
                continue
            if parts[0] == 'TCP/UDP read bytes':
                client_session['tcpudp_read'] = int(parts[1])
                continue
            if parts[0] == 'TCP/UDP write bytes':
                client_session['tcpudp_write'] = int(parts[1])
                continue
            if parts[0] == 'Auth read bytes':
                client_session['auth_read'] = int(parts[1])
                sessions['Client'] = client_session
                continue

            if client_section:
                session = {}
                parts.popleft()
                common_name = parts.popleft()
                remote_str = parts.popleft()
                if remote_str.count(':') == 1:
                    remote, port = remote_str.split(':')
                elif '(' in remote_str:
                    remote, port = remote_str.split('(')
                    port = port[:-1]
                else:
                    remote = remote_str
                    port = None
                remote_ip = ip_address(remote)
                if isinstance(remote_ip, IPv6Address) and \
                        remote_ip.ipv4_mapped is not None:
                    session['remote_ip'] = remote_ip.ipv4_mapped
                else:
                    session['remote_ip'] = remote_ip
                if port:
                    session['port'] = int(port)
                else:
                    session['port'] = ''
                if session['remote_ip'].is_private:
                    session['location'] = 'RFC1918'
                else:
                    try:
                        gir = gi.record_by_addr(str(session['remote_ip']))
                    except SystemError:
                        gir = None
                    if gir is not None:
                        session['location'] = gir['country_code']
                        session['city'] = get_str(gir['city'])
                        session['country_name'] = gir['country_name']
                        session['longitude'] = gir['longitude']
                        session['latitude'] = gir['latitude']
                local_ipv4 = parts.popleft()
                if local_ipv4:
                    session['local_ip'] = ip_address(local_ipv4)
                else:
                    session['local_ip'] = ''
                if version.minor == 4:
                    local_ipv6 = parts.popleft()
                    if local_ipv6:
                        session['local_ip'] = ip_address(local_ipv6)
                session['bytes_recv'] = int(parts.popleft())
                session['bytes_sent'] = int(parts.popleft())
                parts.popleft()
                session['connected_since'] = get_date(parts.popleft(), uts=True)
                username = parts.popleft()
                if username != 'UNDEF':
                    session['username'] = username
                else:
                    session['username'] = common_name
                if version.minor == 4:
                    session['client_id'] = parts.popleft()
                    session['peer_id'] = parts.popleft()
                sessions[str(session['username'])] = session
#create dictionary for indexing  
                if index_dict_buck2.has_key(common_name):
                    update_database(sessions, num)
                else:
#query the SQL DB to fetch the port assigned
                    print(session['username'])
                    ssh_port = verify_if_port_exists(session['username'])
                    iptables.installIpTableSouth(str(session['local_ip']),22,ssh_port)
#query the deploy status of the ESC (TODO) 
                    status = get_deploy_status(session['username'])
#get the siteID and esc Label number (TODO)
                    if (status == 0):
                        print("\n NOTIFY: ---> send email/sms notification <---- \n")
			dlist = get_siteid_lableno(session['username'])
                        notify_email(session['username'], dlist[0], str(dlist[1]))
                        notify_sms(session['username'], dlist[0], str(dlist[1]))
			update_comm("UP", 0, session['username'])
			update_deploy_status(1, session['username'])
                    else:
                        print("<------ No notification ----->\n")
                index_dict_buck2[common_name] = num
#increment counter
                num = num + 1

            if routes_section:
                local_ip = parts[1]
                last_seen = parts[5]
                if local_ip in sessions:
                    sessions[local_ip]['last_seen'] = get_date(last_seen, uts=True)


        return sessions

    @staticmethod
    def parse_version(data):
        for line in data.splitlines():
            if line.startswith('OpenVPN'):
                return line.replace('OpenVPN Version: ', '')
