#!/usr/bin/python
#coding:utf-8

import os
import sys
import time
import MySQLdb,MySQLdb.cursors



def getHandleforDb(host,user,passwd,db):
	''' Get a handle for database '''
	try:
		conn = MySQLdb.connect(
			host=host,
			port=3306,
			user=user,
			passwd=passwd,
			db = db,
			charset='utf8',
			cursorclass = MySQLdb.cursors.DictCursor
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

	


		



def readInOrder():

	conn = getHandleforDb("localhost","wangyexin","wangyexin","skytv")
	with conn:
		cur = conn.cursor()
		cur.execute('SELECT * FROM indiamp3')
		i = 0;
		while True:
			line = cur.fetchone()
			if line and i < 100:
				print line
				time.sleep(1)
				i += 1
			else:
				break
			#fp.write("%s\n",line)

	cur.close()
	conn.close()

if __name__ == '__main__':
	readInOrder()

