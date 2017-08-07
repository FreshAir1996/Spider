#!/usr/bin/python
#coding:utf-8

import re
import os
import sys
import ctypes
import MySQLdb
import datetime
import warnings
import multiprocessing as mul
from getResource import get_album_to_local,getInfoQuickly

warnings.filterwarnings("ignore")


def getHandleforDb(name):

    conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db = name,
            charset='utf8'
            )
    return conn

def main():
	PATH = '../resource/indiamp3.txt'
	Url = 'https://www.indiamp3.com/'

	if not os.path.getsize(PATH):
		print "Get resources;please wait........"
		get_album_to_local(Url,PATH)
		print "Download success. Start to spider"

	else:
		print "Continue the previous download"
		

	conn = getHandleforDb("skytv")
	cur = conn.cursor()
	with open("tmp.sql","a+") as fw:
		with open(PATH,"r") as fr:
			for string in fr:
				resources = getInfoQuickly(string.strip('\n'),cur)
				os.system("sed -i -e '1d' %s" % PATH)
				if len(resources):
					resources = resources[:-2] + ";" + resources[-1:]
					try:
						sql = "insert into test values \n%s" % resources
						cur.execute(sql)
					except Exception as e:
						print "Save failed as %s" % e
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

