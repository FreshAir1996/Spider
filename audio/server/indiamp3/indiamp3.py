#!/usr/bin/python
#coding:utf-8
import os
import sys
import time
import FFmpeg
import warnings

import requests
import datetime
import MySQLdb,MySQLdb.cursors

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

FFmpeg.init()

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

def download(dic):
	
	floder = os.environ['HOME'] +'/iptv/audio/'+ "%s/%s/" % (dic['category'],dic['albumname'])
#	print floder

	if not os.path.exists(floder):
		os.makedirs(floder)

	dic['local_url_l'] = ''
	dic['local_url_h'] = ''
	dic['local_cover'] = os.environ['HOME'] + '/iptv/audio/cover/notavailable.gif'

	
	if not FFmpeg.getInfo(dic['url_l']):
		name_l = floder + dic['songname'] + '.mp3'
		print name_l

		r = requests.get(dic['url_l'])
		try:	
			with open(name_l,"wb") as codel:
				codel.write(r.content)
		except IOError:
			if dic['songname'].find('/') != -1:
				dic['songname'] = dic['url_l'].split('/')[-1].split('.')
				name_l = floder + dic['url_l'].split('/')[-1]
				print name_l
				
				with open(name_l,"wb") as codel:
					codel.write(r.content)

		dic['local_url_l'] = name_l


	if not FFmpeg.getInfo(dic['url_h']):
		name_h  = floder + dic['songname'] + '(320kbps).mp3'
		print name_h

		r = requests.get(dic['url_h'])
		try:	
			with open(name_h,"wb") as codel:
				codel.write(r.content)
		except IOError:
			if dic['songname'].find('/') != -1:
				dic['songname'] = dic['url_h'].split('/')[-1].split('.')
				name_l = floder + dic['url_h'].split('/')[-1]
				print name_h
				
				with open(name_h,"wb") as codeh:
					codeh.write(r.content)

		

	if dic['cover'].find('.gif') == -1 :
		jpgname = floder + dic['cover'].rsplit("/",1)[-1]
		print jpgname

		r = requests.get(dic['cover'])
		with open(jpgname,"wb") as code:
			code.write(r.content)

		dic['local_cover'] = jpgname

	return dic


def test(Tname,Fsql):
	Start = datetime.datetime.now()
	
	conn = getHandleforDb("localhost","wangyexin","wangyexin","skytv")
	with conn:
		cur1 = conn.cursor()
		cur2 = conn.cursor()
		cur3 = conn.cursor()

#		cur1.execute('SELECT * FROM indiamp3')
		cur1.execute("SELECT * FROM %s WHERE albumname='Mix Collection'" % Tname)
		i = 0
		while True:
			dic = cur1.fetchone()
			if dic:
				if dic['download'] == 'N':
					dic = download(dic)
#					print dic
					update = "UPDATE indiamp3 SET download='Y' where no=%d" % dic['no']
					cur2.execute(update)
					insert = ( 'insert into music value("","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'
					% (dic['category'],dic['albumname'],dic['bitrate'],dic['cover'],dic['songname'],dic['singer'],dic['url_h']
					,dic['url_l'],dic['local_cover'],dic['local_url_l'],dic['local_url_h'])
					)
					cur3.execute(insert)
					Fsql.write(insert + '\n')
					Fsql.flush()
					i += 1
					print "Download %d Mp3 Success !!!" % i
			else:
				break
			


		cur1.close()
		cur2.close()

	End = datetime.datetime.now()

	print End - Start

    

if __name__ == '__main__':
	with open('../sql/indiamp3.sql','a+') as fp:
		test('indiamp3',fp)
	

