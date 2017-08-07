#!/usr/bin/python
#coding:utf-8

import os
import time
import signal
import MySQLdb
import datetime
import warnings
import threading
from getResource import get_album_to_local,getInfoQuickly

warnings.filterwarnings("ignore")

#rule_album = r'<a href="(https://www.indiamp3.com/.*?)"'
#album_re = re.compile(rule_album)

DelLock = threading.Lock()
WriteLock = threading.Lock()
tAll = []

def myHandler(signum,frame):
	for t in tAll:
		t.stop()
	fr.close()
	fw.close()
	print "\nCtrl-C;Interrupt this process"
	exit()
	
	
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


class ReadAndDel(threading.Thread):
	def __init__(self,fun,cur):
		super(ReadAndDel,self).__init__()
		self.fun = fun
#		self.conn = conn
#		self.cur = self.conn.cursor()
		self.cur = cur
		self.thread_stop = False

	def run(self):
		global fr,fw
		string = ''
		resources = ''
		print "%s --- Start" % self.name
		while not self.thread_stop:
			with DelLock:
				try:
					string = fr.next().strip('\n')
#					print string , "--%s" % self.pid
				except StopIteration:
					print "File End!!!"
					for t in tAll:
						t.stop()
					
			if len(string):
				resources = self.fun(string,self.cur)
			
			if len(resources):
				resources = resources[:-2] + ";" + resources[-1:]
				with WriteLock:
					try:
						sql = "insert into music values \n%s" % resources
						self.cur.execute(sql)
#						self.conn.commit()
					except Exception as e:
						print "Insert failed"       # write a log!!
					else:
						os.system("sed -i -e '1d' %s" % PATH)
						fw.write(sql)
						fw.flush()
		
		print "%s ---- End" % self.name

	def stop(self):
		self.thread_stop = True



def main():
	signal.signal(signal.SIGINT,myHandler)
	global PATH
	global fr,fw
	
	PATH = '../resource/indiamp3.txt'
	Url = 'https://www.indiamp3.com'

	if not os.path.getsize(PATH):
		print "Get resources;please wait........"
		get_album_to_local(Url,PATH)
		print "Download success. Start to spider"

	else:
		print "Continue the previous download"
		

	fr = open(PATH,"r")
	fw = open("./tmp.sql","a+")

	conn = getHandleforDb("skytv")
	cur = conn.cursor()
	for i in range(5):
		thd = ReadAndDel(getInfoQuickly,cur)
		thd.setDaemon(True)
		tAll.append(thd)

	for t in tAll:
		t.start()

	while True:
		time.sleep(1)
		if threading.active_count() == 1:
			break;

	fr.close()
	fw.close()
	print  "All Spider is over"
    


if __name__ == '__main__':

	Start = datetime.datetime.now()
	main()
	End = datetime.datetime.now()

	print End - Start
