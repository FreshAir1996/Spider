#!/usr/bin/python
#coding:utf-8
import os
import sys
import time
import FFmpeg
import warnings
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
		
		ret = ( cur.execute('insert into album value("","%s","%s","%s","%s","%s")'  %
				(dic['category'],dic['albumname'],dic['bitrate'],dic['cover'],dic['local_cover'])
				)
			)

	if not FFmpeg.getInfo(dic['url_l']):
		local_url_l = localdir + dic['songname'] + '.mp3'
		dest = myReplace(local_url_l)

		r = requests.get(dic['url_l'])
		with open("1.mp3","wb") as codel:
			codel.write(r.content)

#		print local_url_l
		dic['local_url_l'] = local_url_l

		mp.F_scp('1.mp3',dest)

	if not FFmpeg.getInfo(dic['url_h']):
		local_url_h  = localdir + dic['songname'] + '(320kbps).mp3'
		dest = myReplace(local_url_h)

		r = requests.get(dic['url_h'])
		with open(name_h,"wb") as codeh:
			codeh.write(r.content)
#		print local_url_h
		dic['local_url_h'] = local_url_h
		mp.F_scp('1.mp3',dest)

	ret = ( cur.execute('insert into music value("","%s","%s","%s","%s","%s","%s","%s")'
			% (dic['albumname'],dic['songname'],dic['singer'],dic['url_h'],dic['url_l'],
				dic['local_url_h'],dic['local_url_l']) )
			)
	return dic


def test():
	Start = datetime.datetime.now()
	isExist = ['isExist',None]

	conn_local = getHandleforDb("localhost","wangyexin","wangyexin","skytv")
	conn_server = getHandleforDb("85.25.46.133","wangyexin","wangyexin","skytv")

	mp = mypexpect.MyPexpect('root','85.25.46.133','tv11Mar2015')
	with conn_local:
		cur1 = conn_local.cursor()
		cur2 = conn_local.cursor()
		cur_server = conn_server.cursor()

		cur1.execute('SELECT * FROM indiamp3')
#		cur1.execute("SELECT * FROM indiamp3 WHERE albumname='1920 (2008)'")
		i = 0
		while True:
			dic = cur1.fetchone()
			if dic:
				if dic['download'] == 'N':
				
					dic = download(dic,cur_server,mp,isExist)
#					print dic
					update = "UPDATE indiamp3 SET download='Y' where no=%d" % dic['no']
					cur2.execute(update)

					i += 1
					print "Download %d Mp3 Success !!!" % i
			else:
				break
			


		cur1.close()
		cur2.close()
		cur3.close()

	End = datetime.datetime.now()

	print End - Start

    

if __name__ == '__main__':
	test()

	str1 = 'hello'
	str2 = 'hello'

	print str1==str2
	

