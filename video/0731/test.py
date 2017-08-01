#!/usr/bin/python
#coding:utf-8

import os
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

		return self.categorys

	def saveIntoText(self,fw):
		for child in self.categorys:
			tmpstring = ''
			for movie in child:
				try:
					tmpstring +=( "'%s','%s','%s','%s'\n" %
						(child['name'],movie['name'],movie['link'],movie['picture']))
				except TypeError:
					continue

			fw.write(tmpstring)
	


		

def download(url,name):
	mkv = name.split('/')[-1]
	child = subprocess.Popen(["wget","-O",mkv,url])
	child.communicate()
	return 0

def save_to_loacl(tag,path,conn):
	cur = conn.cursor()
	if path[-1] == '/':
		floder = path + str(tag['name'])+ '/'
	else:
		floder = path +'/' + str(tag['name']) + '/'
	
#	if not os.path.exists(floder):
#		os.makedirs(floder)
	
#	os.chdir(floder)
	tmp = ''
	for movie in tag:
		try:
			name_movie = floder + movie['name']+ '/' 
			name_pic = name_movie + movie['picture'].split('/')[-1]
			if not os.path.exists(name_movie):
				os.makedirs(name_movie)
			
			os.chdir(name_movie)
			print os.getcwd()
			sql =( "select * from iptv_movies where category='%s' and videoname='%s'" 
					%  (tag['name'],movie['name']))
			if cur.execute(sql):
				pass 
			else:
				name_movie = name_movie + movie['name'] + ".mkv"
				download(movie['link'],name_movie)
			
				tmp +=("('','%s','%s','%s','%s','%s','%s'),\n" %
					(tag['name'],movie['name'],movie['link'],movie['picture'],name_movie,name_pic))
	

		except TypeError :
			continue
	try:
		if len(tmp):
			sql = "insert into iptv_movies values \n " + tmp[:-2] + ";" 
			cur.execute(sql)
	except Exception as e:
		print e




if __name__ == '__main__':
	with open("./goldentv.xml","r") as fr:
		cate = Category(fr)
		tags = cate.getCategory()
#		print tags[2]
	path = os.getcwd()
	conn = getHandleforDb('skytv')

	save_to_loacl(tags[2],path,conn)

