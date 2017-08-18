#!/usr/bin/python
#coding:utf-8

import re
import os
import sys
import ctypes
import MySQLdb
import logging
import datetime
from mylogger import Logger
import warnings
import multiprocessing as mul
from getResource import get_album_to_local,getInfoQuickly

warnings.filterwarnings("ignore")


def getHandleforDb(host,user,passwd,db):
	''' Get a handle for database '''
	try:
		conn = MySQLdb.connect(
			host=host,
			port=3306,
			user=user,
			passwd=passwd,
			db = db,
			charset='utf8'
			)
	except MySQLdb.Error,e:
		if e[0] == 1044:
			print 'Connect database failed,Maybe there no tables'
		elif e[0] == 1045:
			print 'Connect database failed,please confirm account or passwd'
		else:
			print e
		sys.exit()
	else:
		return conn


def main():
	PATH = '../resource/indiamp3.txt'
	Url = 'https://www.indiamp3.com/'

	log = Logger('../log/indiamp3.log',logging.DEBUG,logging.WARNING)
	fmt = logging.Formatter('%(message)s')
	log.setStreamFmt(fmt)

	if not os.path.getsize(PATH):
		print "WARNING: Get resources now.Don't interrupt"
		get_album_to_local(Url,PATH,log)
		print "Download success. Start to spider"

	else:
		print "Continue the previous download"
		

	conn = getHandleforDb("localhost","wangyexin","wangyexin","skytv")
	cur = conn.cursor()
	with open("../sql/indiamp3.sql","a+") as fw:
		with open(PATH,"r") as fr:
			for string in fr:
				url = string.strip('\n')
				resources = getInfoQuickly(url,cur,log)
				os.system("sed -i -e '1d' %s" % PATH)
				if len(resources):
					resources = resources[:-2] + ";" + resources[-1:]
					try:
						sql = "insert into indiamp3 values \n%s" % resources
						cur.execute(sql)
					except Exception as e:
						log.exception("Fail Insert (%s)" % url)
					else:
						fw.write(sql)
						fw.flush()


	cur.close()
	conn.close()
		


if __name__ == '__main__':
	Start = datetime.datetime.now()
	main()
	End = datetime.datetime.now()

	print End - Start

