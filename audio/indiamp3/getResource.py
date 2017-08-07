#!/usr/bin/python
#coding:utf-8
import re
import os
import sys
import FFmpeg
import warnings
from bs4 import BeautifulSoup
import requests
import datetime
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')

warnings.filterwarnings("ignore")
rule_info = r'\{(.*?)\}'
info_re = re.compile(rule_info)
FFmpeg.init()

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

def get_categories_of_web(url):
	categories = []
	try:
		req = requests.get(url)
	except requests.RequestException:
		print "Cannot request to %s"  % url  # should write a log!!
	else:
		soup = BeautifulSoup(req.text,"html.parser")
		categories =        \
		soup.findAll('a',attrs={'href':re.compile(r'https://www.indiamp3.com/list/.*?')})
	
	return categories

def get_album_of_category(url):
	
	albums = []
	try:
		req = requests.get(url)
	except requests.RequestException:
		print "Cannot request to %s"  % url  # should write a log!!
	else:
		soup = BeautifulSoup(req.text,"html.parser")
		albums = soup.findAll('a',attrs={'rel':'nofollow','href':re.compile(r'.*?-mp3-songs')})

	return albums
			
def get_album_to_local(url,path):
	
	categories = get_categories_of_web(url)
	with open(path,'w+') as fp:
		for category in categories:
			for album in get_album_of_category(category['href']):
				fp.write(str(album['href']) + '\n')

	



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
def get_info_for_album(url,dic):
	floder = None
	soup = None
	headers = {
    'authority':'www.indiamp3.com',\
    'path':'/%s' % url.split("/")[-1],\
    'scheme':'https',\
    'referer':'https://www.indiamp3.com/',\
    'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
	try:
		req = requests.get(url,headers=headers,timeout=10)
	except requests.RequestException:
		print "requests (%s) failed................" % url
		return soup,floder
	except Exception,e:
		print "get %s failed as %s" % (url,e)
		return soup,floder
	else:
		if req.status_code >= 400:
			print "This page does not exist"
		else:
			soup = BeautifulSoup(req.text,"html.parser")
			table = soup.find("table",attrs={'width':'100%','class':'album_bg'})
			category =  table.select('a')[0].text
			dic['category'] = category

			albumname = table.find("b",text=re.compile(r'Album Name:(.*?)')).text.split(":")[-1].strip()
			dic['albumname'] = albumname

			floder = os.environ['HOME'] +'/iptv/audio/'+ "%s/%s/" % (category,albumname)
			print floder

			if not os.path.exists(floder):
				os.makedirs(floder)
			if table.select('p'):
				dic['bitrate'] = '128/320kbps'
			else:
				dic['bitrate'] = '128kbps'

			image = table.tr.td.img['src']
			if image.find('.gif') == -1:
				jpgname = floder + image.rsplit("/",1)[-1]
				cover =  add_head_url(image).replace(" ","%20")
				r = requests.get(cover)
				with open(jpgname,"wb") as code:
					code.write(r.content)
			else:
				jpgname = os.environ['HOME'] + '/iptv/audio/cover/notavailable.gif'
				cover = add_head_url(image)
			
			#else:
			#	print 'Exist'

			
			dic['cover'] = cover
			dic['local_cover'] = jpgname
		

		return soup,floder
	
#获得某个音乐的部分信息 songname singer url_h url_l 以单个专辑为目标
def getInfoQuickly(url,cur):
#	print "Start get Resources from %s" % url
	pwd = os.getcwd()
	tempstring = ''
	dic = {}
	soup_album,floder = get_info_for_album(url,dic)
	if soup_album == None or floder==None:
		return tempstring
	os.chdir(floder)
	headers = {
	'authority':'www.indiamp3.com',\
#	'path':'',\
	'scheme':'https',\
	'referer':url,\
	'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36\
	(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
	names = soup_album.findAll(href=re.compile(r'javascript:playSong.*?'))
	links = soup_album.findAll(href=re.compile(r'download-song.php\?song=\d{1,6}'))
	
	sql = "select * from music where albumname='%s' " % dic['albumname']
	ret = cur.execute(sql)
	if ret:
		pass
	else:

		if dic['bitrate'] == '128/320kbps':            # 判断是否有两个码率
			for i in range(len(names)/2):         #有两个码率，则可以折半读取网页 

	#获得音乐链接
#				headers['path'] = links[2*i]['href']
#				link = add_head_url(headers['path'])
				link = add_head_url(links[2*i]['href'])
				try:
					r = requests.get(link,headers=headers,timeout=15)
				except Exception,e:
					print "Failed Down (%s) " % link
				else:
					soup_song = BeautifulSoup(r.text,"html.parser")
					relative_addr = soup_song.find('source')['src'].replace(" ","%20")
					absolute_addr = add_head_url(relative_addr)
	#判断音乐链接是否有效
					infos = FFmpeg.getInfo(absolute_add)
					if len(infos):
						result = re.findall(info_re,infos)
						try:
							dic['songname'] = result[0].split(":")[-1].split('@')[0].strip()
							dic['singer'] = result[1].split(":")[-1].split('@')[0].strip()
						except :
							print "############"
							continue
					
						sql = ("select * from music where songname='%s' and singer='%s' " 
								% (dic['songname'],dic['singer']))
						if cur.execute(sql):
							pass
						else:
							
							dic['url_h'] = absolute_addr.replace("(128%20Kbps)","(320%20Kbps)")
							dic['url_l'] = absolute_addr
							name_l = floder + dic['songname'] +'.mp3'
							name_h = name_l[:-4]+ '(320kbps)' + name_l[-4:]
							dic['local_url_h'] = name_h
							dic['local_url_l'] = name_l
							print ("Start Download Music From (%s,%d)"  % (url,i))
							r = requests.get(dic['url_l'])
							with open(name_l,"wb") as codel:
								codel.write(r.content)
							r =requests.get(dic['url_h'])
							with open(name_h,"wb") as codeh:
								codeh.write(r.content)
							tempstring +=("('','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'),\n" %
				(dic['category'],dic['albumname'],dic['bitrate'],dic['cover'],
			 dic['songname'],dic['singer'],dic['url_h'],dic['url_l'],dic['local_cover'],dic['local_url_l'],dic['local_url_h']))
#				print dic
		else:
			for i in range(len(names)):
#				headers['path'] = links[i]['href']
#				link = add_head_url(headers['path'])
				link = add_head_url(links[i]['href'])
				try:
					r = requests.get(link,headers = headers,timeout=15)
				except Exception,e:
					print e
				else:
					soup_song = BeautifulSoup(r.text,"html.parser")
					relative_addr = soup_song.find('source')['src'].replace(" ","%20")
					absolute_addr = add_head_url(relative_addr)
					infos = FFmpeg.getInfo(absolute_addr)
					if len(infos):
						result = re.findall(info_re,infos)
			
						try:
							dic['songname'] = result[0].split(":")[-1].split('@')[0].strip()
							singer =( result[1].split(":")[-1].split('@')[0].strip() )
							dic['singer'] = singer.decode('utf-8')
						except Exception as e:
							print "$$$$$$$$$$$$ %s" % e
							continue

						sql = ("select * from music  where songname='%s' and singer='%s'" 
								% (dic['songname'],dic['singer']))
						ret = cur.execute(sql)
						if ret:
							pass
						else:
							dic['url_h'] = ''
							dic['local_url_h'] = ''
							dic['url_l'] = absolute_addr
							name_l = floder + dic['songname'] +'.mp3'
							dic['local_url_l'] = name_l
							print ("Start Download Music From (%s,%d)" % (url,i))
							tempstring +=("('','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'),\n" %
			(dic['category'],dic['albumname'],dic['bitrate'],dic['cover'],
			dic['songname'],dic['singer'],dic['url_h'],dic['url_l'],dic['local_cover'],dic['local_url_l'],dic['local_url_h']))
							r = requests.get(dic['url_l'],headers=headers)
							with open(name_l,"wb") as code:
								code.write(r.content)
			
#				print dic
        
#	print "End get Resources from %s" % url

	os.chdir(pwd)
	return tempstring

def test(url,fp):
	Start = datetime.datetime.now()
	conn = getHandleforDb("skytv")
	cur = conn.cursor()

	resources = getInfoQuickly(url,cur)
	if len(resources):
		resources = resources[:-2] + ";" + resources[-1:]
		try:
			sql = "insert into test values \n%s" % resources
			cur.execute(sql)
		except Exception as e:
			print "Save failed as %s" % e
		else:
			fp.write(sql)

	cur.close()
	conn.close()
	fp.close()
	
	End = datetime.datetime.now()
	print Start
	print End

    

if __name__ == '__main__':
	Start = datetime.datetime.now()
	with open("../resource/indiamp3.txt","w+") as fp:
		for album in get_album_of_category('https://www.indiamp3.com/list/X'):
			fp.write(str(album['href'])+'\n')

	End = datetime.datetime.now()

	print End - Start

