#!/usr/bin/python
#coding:utf-8
import os
import sys
import time
import FFmpeg
import warnings
import logging
from mylogger import Logger
import mypexpect
import requests
import datetime
import MySQLdb,MySQLdb.cursors

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

FFmpeg.init()

isExist = 'isExist'
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

def myReplace(string):

	if string.rfind('(') != -1:
		string = string.replace('(','\(').replace(')','\)')

	if string.rfind(' ') != -1:
		string = string.replace(' ','\ ')
	
	if string.rfind('&') != -1:
		string = string.replace('&','\&')

	return string

def download(dic,cur,mp,isExist):
	
	dic['local_url_l'] = ''
	dic['local_url_h'] = ''
	dic['local_cover'] = '/home/iptv/audio/cover/notavailable.gif'

	localdir = '/home/iptv/audio/'+ "%s/%s/" % (dic['category'],dic['albumname'])

	if isExist[0] == localdir:
		pass
	else:
		isExist[0] = localdir
		floder= myReplace(localdir)
#		print floder
		mp.F_ssh('mkdir -p %s' % floder)

		if dic['cover'].find('.gif') == -1 :
			local_cover = localdir + dic['cover'].rsplit("/",1)[-1]
			dest = myReplace(local_cover)
#			print local_cover

			r = requests.get(dic['cover'])
			with open('1.jpg',"wb") as code:
				code.write(r.content)

			mp.F_scp('1.jpg',dest)
			dic['local_cover'] = local_cover
		try:
			ret = ( cur.execute('insert into album value("","%s","%s","%s","%s","%s")'  %
				(dic['category'],dic['albumname'],dic['bitrate'],dic['cover'],dic['local_cover'])
				)
			)
		except Exception as e:
			raise e
			return -1

	if FFmpeg.getMp3Info(dic['url_l']):
		local_url_l = localdir + dic['songname'] + '.mp3'
		dest = myReplace(local_url_l)

		r = requests.get(dic['url_l'])
		with open("1.mp3","wb") as codel:
			codel.write(r.content)

#		print local_url_l
		dic['local_url_l'] = local_url_l

		mp.F_scp('1.mp3',dest)

	if FFmpeg.getMp3Info(dic['url_h']):
		local_url_h  = localdir + dic['songname'] + '(320kbps).mp3'
		dest = myReplace(local_url_h)

		r = requests.get(dic['url_h'])
		with open(name_h,"wb") as codeh:
			codeh.write(r.content)
		print local_url_h
		dic['local_url_h'] = local_url_h
		mp.F_scp('1.mp3',dest)

	try:
		ret = ( cur.execute('insert into music value("","%s","%s","%s","%s","%s","%s","%s")'
			% (dic['albumname'],dic['songname'],dic['singer'],dic['url_h'],dic['url_l'],
				dic['local_url_h'],dic['local_url_l']) )
			)
	except Exception as e:
		raise e
		return -1
	
	return 0


def test():
	Start = datetime.datetime.now()
	isExist = ['isExist',None]

	conn_local = getHandleforDb("localhost","wangyexin","wangyexin","skytv")
	conn_server = getHandleforDb("149.202.75.184","wangyexin","wangyexin","skytv")

	log = Logger('../log/indiamp3.log',logging.DEBUG,logging.WARNING)
	fmt = logging.Formatter('%(message)s')
	log.setStreamFmt(fmt)
	mp = mypexpect.MyPexpect('root','149.202.75.184','pY8w4jPisL8y')

	with conn_local:
		cur_local_1 = conn_local.cursor()
		cur_local_2 = conn_local.cursor()
		cur_server = conn_server.cursor()

		cur1.execute('SELECT * FROM indiamp3')
#		cur1.execute("SELECT * FROM indiamp3 WHERE albumname='1920 (2008)'")
		i = 0
		while True:
			dic = cur_local_1.fetchone()
			if dic:
				if dic['download'] == 'N':
					try:
						download(dic,cur_server,mp,isExist)
					except Exception:
						log.exception("Insert Fail due to")
#					print dic
					else:
						update = "UPDATE indiamp3 SET download='Y' where no=%d" % dic['no']
						cur_local_2.execute(update)

						i += 1
						log.info("Download %d Mp3 Success !!!" % i)
			else:
				break
			


		cur_local_1.close()
		cur_local_2.close()
		cur_server.close()

	End = datetime.datetime.now()

	print End - Start

    

if __name__ == '__main__':
	test()

	str1 = 'hello'
	str2 = 'hello'

	print str1==str2
	

