#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# poraenv (c) 2017 by Andre Karlsson<andre.karlsson@protractus.se>
#
# This file is part of pyorabackup.
#
#    poraenv is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    poraenv is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with poraenv.  If not, see <http://www.gnu.org/licenses/>.
#
# Filename:  by: andrek
# Timesamp: 3/27/17 :: 9:06 AM

from subprocess import Popen, PIPE
from re import split
from sys import stdout
from datetime import *
import pprint
import glob
import re
import platform
import os
import socket
import getpass


def singleton(class_):
	instances = {}

	def getinstance(*args, **kwargs):
		if class_ not in instances:
			instances[class_] = class_(*args, **kwargs)
		return instances[class_]

	return getinstance


class Database(object):
	def __init__(self, sid, ohome):
		#super(Database, self).__init__()
		self.sid = sid
		self.ohome = ohome
		#print 'Setting DB thingy', sid, ohome

	def __repr__(self):
		return 'Database(Oracle_SID=%s, Oracle_HOME=%s)' % (self.sid, self.ohome)

	def __str__(self):
		return 'Database(Oracle_SID=%s, Oracle_HOME=%s)' % (self.sid, self.ohome)

	def getsid(self):
		return self.sid

	def getohome(self):
		return self.ohome

	def setenv(self):
		os.putenv('ORACLE_SID', self.sid)
		os.putenv('ORACLE_HOME', self.ohome)
		os.putenv('PATH', os.environ['PATH'] + ':/usr/bin:/usr/sbin:' + self.ohome + '/bin:/opt/csw/bin')

		#print self.sid
		#print('Setting ORACLE_HOME {}').format(self.ohome)

	def getenv(self):
		if os.environ['ORACLE_HOME'] or os.environ['ORACLE_SID']:
			return os.environ['ORACLE_SID'], os.environ['ORACLE_HOME']
		else:
			return None

	def getDB(self):
		return Database


@singleton
class Logging(object):
	def __init__(self, dir,
	             ldate=datetime.today().strftime("%Y%m%d_%H%M")):
		self.logdir = dir
		self.envlogdir = dir + 'env_' + '_' + ldate + '.log'
		#print self.envlogdir

	@property
	def logDir(self):
		return self.logdir

	@logDir.setter
	def logDir(self, newdir):
		self.logdir = newdir

	@property
	def envlogDir(self):
		return self.envlogdir

	@envlogDir.setter
	def envlogDir(self, newdir):
		self.envlogdir = newdir


def getystem():
	return platform.system().lower()


def parseoratab(fname):
	config = {}
	with open(fname, "r") as f:
		for line in f.readlines():
			li = line.lstrip().lower()
			if li and not li.startswith("#") and not li.startswith("+") and not li.startswith("-"):
				linesplit = li.split(':')
				initfiles = glob.glob(linesplit[1]+'/dbs/init*.ora')
				for initfile in initfiles:
					if linesplit[0].lower() in initfile.lower():
						sid = re.search(linesplit[1]+'/dbs/init(.*).ora', initfile.lower())

				config[sid.group(1)] = [linesplit[1]]
	return config


def getoratab(ostype):
	if 'sunos' in ostype and os.path.exists('/var/opt/oracle/oratab'):
		#print ostype
		return '/var/opt/oracle/oratab'
	elif 'linux' in ostype and os.path.exists('/etc/oratab'):
		return '/etc/oratab'
	else:
		return 'none'
		#raise ValueError('oratab not found')


if __name__ == "__main__":
	databases = []
	mysystem = getystem()
	#print mysystem
	hostname = socket.gethostname()
	#print(hostname)
	yearweek = datetime.today().strftime("%Y%U")
	logdate = datetime.today().strftime("%Y%m%d_%H%M")
	#print logdate

	log = Logging((os.path.abspath(__file__)) + "log/" + yearweek)
	oratab = getoratab(mysystem)
	installed_db_lst = parseoratab(oratab)

	for key, value in installed_db_lst.iteritems():
		databases.append(Database(key.upper(), value[0]))

	#pp.pprint(databases)

	while True:
		os.system('clear')
		for idx in range(0, len(databases)):
			print '  ', idx, '            ', databases[idx]

		selection = raw_input('Please select: ')

		if int(selection) > len(databases) or int(selection) < 0:
			print ('Unknown input')
			continue
		else:
			databases[int(selection)].setenv()
			print 'Oracle DB is now set as {}'.format(databases[int(selection)].getsid())
			bash = 'bash --rcfile <(echo "typeset +x PS1="POraEnv::%s{$ORACLE_SID}@%s:\\$ "") -i' % (getpass.getuser(), hostname)
			os.system(bash)
			break
