#!/usr/bin/python
#coding:utf-8

import os
import time
import MySQLdb
import warnings
import subprocess
from bs4 import BeautifulSoup

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

def down_by_wget(url,name):
	mkv = name.split('/')[-1]
	child = subprocess.Popen(["wget","-O",mkv,url])
	child.communicate()
	return 0


def down_by_curl(url,name):
	jpg = name.split('/')[-1]
	child = subprocess.Popen(["curl","-o",jpg,url])
	child.communicate()
	return 0

class Category():
	def __init__(self,fr):
		self.fp = fr
		self.categorys = []

	def getCategory(self):
		soup = BeautifulSoup(self.fp,"xml")
		categorys = soup.find_all('category')
		for category in categorys:
			if str(category.movie['link']).find('.mkv') != -1:
				self.categorys.append(category)


	def save(self,tag,path,conn):
		cur = conn.cursor()
		if path[-1] == '/':
			floder = path + str(tag['name'])+ '/'
		else:
			floder = path +'/' + str(tag['name']) + '/'
		
		for movie in tag:
			tmp = ''
			try:
				name_movie = floder + movie['name']+ '/' 
				name_pic = name_movie + movie['picture'].split('/')[-1]
				if not os.path.exists(name_movie):
					os.makedirs(name_movie)
				
				os.chdir(name_movie)
				sql =( "select * from iptv_movies where category='%s' and videoname='%s'" 
						%  (tag['name'],movie['name']))
				if cur.execute(sql):
					pass 
				else:
					name_movie = name_movie + movie['name'] + ".mkv"
					down_by_wget(movie['link'],name_movie)   # You will arrive if your server is abroad
#					down_by_curl(movie['link'],name_movie)
					time.sleep(10)
					down_by_curl(movie['picture'],name_pic)
					time.sleep(3)

					tmp +=("('','%s','%s','%s','%s','%s','%s'),\n" %
						(tag['name'],movie['name'],movie['link'],movie['picture'],name_movie,name_pic))
		

			except TypeError :
				continue

			else:
				if len(tmp):
					sql = "insert into iptv_movies values \n " + tmp[:-2] + ";" 
					cur.execute(sql)
		
		cur.close()


		




if __name__ == '__main__':

	pwd = os.getcwd()

	with open("./goldentv.xml","r") as fr:
		cate = Category(fr)
		cate.getCategory()
#		print tags[2]
	path = os.environ['HOME'] + '/iptv/video/'
	conn = getHandleforDb('skytv')
	for tag in cate.categorys:
		cate.save(tag,path,conn)
	
	conn.close()
	os.chdir(pwd)
