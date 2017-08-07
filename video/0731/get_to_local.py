#!/usr/bin/python
#coding:utf-8

import os
import time
import datetime
import warnings
import subprocess
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

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

def create_table(fp):
	
	with open("./mysql.txt") as fr:
		fp.write(fr.read())
		
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
		
		return self.categorys

	def save(self,tag,path,fw):
		if path[-1] == '/':
			floder = path + str(tag['name'])+ '/'
		else:
			floder = path +'/' + str(tag['name']) + '/'

		fw.write("insert into iptv_movies valuse\n")
		for movie in tag:
			tmp = ''
			try:
				name_movie = floder + movie['name']+ '/' 
				name_pic = name_movie + movie['picture'].split('/')[-1]
				if not os.path.exists(name_movie):
					os.makedirs(name_movie)
				
				os.chdir(name_movie)
				name_movie = name_movie + movie['name'] + ".mkv"
				down_by_wget(movie['link'],name_movie)   # You will arrive if your server is abroad
#					down_by_curl(movie['link'],name_movie)
#					time.sleep(10)
				down_by_curl(movie['picture'],name_pic)
#					time.sleep(3)

				tmp +=("('%s','%s','%s','%s','%s','%s'),\n" %
						(tag['name'],movie['name'],movie['link'],movie['picture'],name_movie,name_pic))
			except TypeError :
				continue
			except Exception as e:
				print "Some Error",e      # should write a log

			else:
				if len(tmp):
					tmp = tmp[:-2] + ";\n" 
					fw.write(tmp)
		


if __name__ == '__main__':
	
	Start = datetime.datetime.now()
	pwd = os.getcwd()

	with open("./goldentv.xml","r") as fr:
		cate = Category(fr)
		tags = cate.getCategory()
		path = os.environ['HOME']+'/iptv/video/'

		with open("./iptv_movies.sql","a+") as fw:
			create_table(fw)
			cate.save(tags[0],path,fw)
	
	os.chdir(pwd)
	End = datetime.datetime.now()

	print End - Start
