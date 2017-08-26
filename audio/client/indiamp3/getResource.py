#!/usr/bin/python
#coding:utf-8
import re
import os
import sys
import FFmpeg
import warnings
import logging
import MySQLdb
from mylogger import Logger
from bs4 import BeautifulSoup
import requests
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

warnings.filterwarnings("ignore")

rule_info = r'\{(.*?)\}'
info_re = re.compile(rule_info)
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


def get_categories_of_web(url,log):
	categories = []
	try:
		req = requests.get(url)
	except requests.RequestException:
		log.exception("Cannot request to %s; it's critical!!" % url) 
		sys.exit(-1)
	else:
		soup = BeautifulSoup(req.text,"html.parser")
		categories =        \
		soup.findAll('a',attrs={'href':re.compile(r'https://www.indiamp3.com/list/.*?')})
	
	return categories

def get_album_of_category(url,log):
	
	albums = []
	try:
		req = requests.get(url)
	except requests.RequestException:
		fmt = logging.Formatter('%(message)s')
		log.setStreamFmt(fmt)
		log.exception("get_album_of_category for (%s) failed; it's terrible" % url)
	else:
		soup = BeautifulSoup(req.text,"html.parser")
		albums = soup.findAll('a',attrs={'rel':'nofollow','href':re.compile(r'.*?-mp3-songs')})

	return albums
			
def get_album_to_local(url,path,log):
	
	categories = get_categories_of_web(url,log)
	with open(path,"w+") as fp:
		for category in categories:
			for album in get_album_of_category(category['href'],log):
				try:
					fp.write(str(album['href']) + '\n')
				except AttributeError,e:
					print 'some error',e
	



#添加绝对路径
def add_head_url(url):
	orignal_url = 'https://www.indiamp3.com/'
	if(url[0] == '/'):
		orignal_url ="https://www.indiamp3.com"
		return orignal_url + url
	elif(url[0] == '.'):
		return orignal_url+url[2:]
	else:
		return orignal_url+url



#获得专辑的部分信息category、albumname、bitrate、cover
def get_info_for_album(url,dic,log):

	soup = None
	headers = {
#    'authority':'www.indiamp3.com',\
#    'path':'/%s' % url.split("/")[-1],\
#    'scheme':'https',\
#    'referer':'https://www.indiamp3.com/',\
    'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
	try:
		req = requests.get(url,headers=headers,timeout=15)
	except requests.RequestException:
		log.error("Failed due to Requests: %s" % url)
		return soup
	except Exception,e:
		log.exception("Failed  due to Exception: %s" % url)
		return soup
	else:
		if req.status_code >= 400:
			print "This page(%s) does not exist " % url
		else:
			soup = BeautifulSoup(req.text,"html.parser")
			table = soup.find("table",attrs={'width':'100%','class':'album_bg'})


			category =  table.select('a')[0].text
			dic['category'] = category

			albumname = table.find("b",text=re.compile(r'Album Name:(.*?)')).text.split(":")[-1].strip()
			dic['albumname'] = albumname
			
			bit = len(table.select('p'))
			if bit == 2:
				dic['bitrate'] = '128/320kbps'
			elif bit == 1:
				dic['bitrate'] = '320kbps'
			else:
				dic['bitrate'] = '128kbps'

#			image = table.tr.td.img['src']
#			cover =  add_head_url(image).replace(" ","%20")
			dic['cover'] = add_head_url(table.tr.td.img['src']).replace(" ","%20")
		
		return soup
	
#获得某个音乐的部分信息 songname singer url_h url_l 以单个专辑为目标
def getInfoQuickly(url,cur,log):
	preName = ''
	tempstring = ''
	dic = {}
	step = 1
	soup_album = get_info_for_album(url,dic,log)
	if soup_album == None :
		return tempstring

	sql = "select * from indiamp3 where albumname = '%s' " % dic['albumname']
	if cur.execute(sql):
		return tempstring
	else:

		headers = {
#		'authority':'www.indiamp3.com',\
#		'scheme':'https',\
#		'referer':url,\
		'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36\
		(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
	
		links = soup_album.findAll(href=re.compile(r'download-song.php\?song=\d{1,6}'))
		names = soup_album.findAll(href=re.compile(r'javascript:playSong.*?'))
#		print names[0].text
	
		if dic['bitrate'] == '128/320kbps':            # 判断是否有两个码率
			step = 2

		for i in range(0,len(links),step):         #通过步长来适用两个码率

			link = add_head_url(links[i]['href'])
			try:
				r = requests.get(link,headers=headers,timeout=10)
			except Exception,e:
				log.warn("Failed Down (%s,%d) " % (url,i))
			else:
				soup_song = BeautifulSoup(r.text,"html.parser")
				relative_addr = soup_song.find('source')['src'].replace(" ","%20")
				absolute_addr = add_head_url(relative_addr)
	#判断音乐链接是否有效
				log.debug("Use FFmpeg")
				infos = FFmpeg.getMp3Info(absolute_addr)
				if len(infos) :
					dic['songname'] = names[i].text
					dic['singer'] = 'Unknown'

					result = re.findall(info_re,infos)
					try:
						songname = result[0].split(":")[-1].split('@')[0].strip()
						singer = result[1].split(":")[-1].split('@')[0].strip()
						if songname and songname.find('/') == -1:
							if songname == preName:
								dic['songname'] = songname + ' - ' + singer
							else:
								dic['songname'] = songname
							
						if singer:
							dic['singer'] = singer

					except :
						print "############"
						continue
					
					else:
						dic['url_h'] = ''
						dic['url_l'] = ''

						if step == 2:

							dic['url_h'] = absolute_addr.replace("(128%20Kbps)","(320%20Kbps)")
							dic['url_l'] = absolute_addr

						else:
							
							if dic['bitrate'] == '320kbps':
								dic['url_h'] = absolute_addr
							else:
								dic['url_l'] = absolute_addr
					
						print dic['songname']
						preName = dic['songname']
						log.info("Get Resources Success From (%s,%d)"  % (url,i))
						tempstring +=('("","%s","%s","%s","%s","%s","%s","%s","%s","N"),\n' %
				(dic['category'],dic['albumname'],dic['bitrate'],dic['cover'],
			 dic['songname'],dic['singer'],dic['url_h'],dic['url_l']))
	
	return tempstring

def test(url,fp,log):
	Start = datetime.datetime.now()
	conn = getHandleforDb("192.168.1.179","wangyexin","wangyexin","skytv")
	cur = conn.cursor()
	resources = getInfoQuickly(url,cur,log)
	if len(resources):
		resources = resources[:-2] + ";" + resources[-1:]
		try:
			sql = "insert into indiamp3 values \n%s" % resources
			cur.execute(sql)
		except Exception as e:
			print "Save failed as %s" % e
		else:
			conn.commit()
			fp.write(sql)

	cur.close()
	conn.close()
	fp.close()
	
	End = datetime.datetime.now()
	print End - Start

    

if __name__ == '__main__':
	Start = datetime.datetime.now()
	log = Logger('temp.log',logging.DEBUG,logging.WARNING)
   	url = 'https://www.indiamp3.com/military-raaj-1998-mp3-songs'
	url = 'https://www.indiamp3.com/mix-collection-mp3-songs'
	url = 'https://www.indiamp3.com/a-flying-jatt-2016-mp3-songs'
	url = 'https://www.indiamp3.com/guest-in-london-2017-mp3-songs'
#	url = 'https://www.indiamp3.com/1920-2008-mp3-songs'
#	url = 'https://www.indiamp3.com/mir-dil-ruba-mp3-songs'
#	url = 'https://www.indiamp3.com'
#	with open('../resource/indiamp3.txt','w+') as fw:
#		get_album_to_local(url,fw,log)	
	with open("./1.sql","w+") as fw:
		test(url,fw,log)

	End = datetime.datetime.now()
	print End - Start

