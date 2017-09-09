#!/usr/bin/python
#coding:utf-8

from urllib2 import urlopen
import json

def get_json_from_url(url):
	response = urlopen(url).read()
	response_json = json.loads(response)
	return response_json;

def make_url_head(dic,s_type):
	http = "http://"
	url = ( http + dic['url'] + ":" + dic['port'] + ("/%s/" % s_type) +
			dic['username'] + "/" + dic['password'] + "/" )
	return url

class ALLStream(object):
	def __init__(self,j_data):
		self.data = j_data
		self.categories_of_live_name = []
		self.categories_of_movie_name = []
		self.infos = {}

	def get_info_without_id(self):
		return self.infos

	def get_server_info(self,*args):
		s_data = self.data.get('server_info')
		for arg in args:
			try:
				value = s_data[arg]
			except KeyError:
				raise KeyError("Server's infomations no key : %s "  % arg)
			else:
				self.infos.setdefault(arg,value)
		return 0
	
	def get_user_info(self,*args):
		s_data = self.data.get('user_info')
		for arg in args:
			try:
				value = s_data[arg]
			except KeyError:
				raise KeyError("User's infomations no key : %s "  % arg)
			else:
				self.infos.setdefault(arg,value)
		return 0
	
	def get_category_of_live(self,rexp=None):
		lives = self.data.get('categories').get('live')
		for live in lives:
			if rexp == None:
				self.categories_of_live_name.append(live.get('category_name'))
			else:
				if live.get('category_name').find(rexp) != -1:
					self.categories_of_live_name.append(live.get('category_name'))
				

		return self.categories_of_live_name

	def get_category_of_movie(self,rexp=None):
		movies = self.data.get('categories').get('movie')
		for movie in movies:
			if rexp == None:
				self.categories_of_movie_name.append(movie.get('category_name'))
			else:
				if movie.get('category_name').find(rexp) != -1:
					self.categories_of_movie_name.append(movie.get('category_name'))
		

		return self.categories_of_movie_name

	def get_live_url(self,category,urlhead):
		channels = data.get('available_channels')
		for channel in channels.values():
			if channel.get('category_name') == category:
				url = urlhead + channel.get('stream_id') + ".ts"
				name = channel.get('name')
				yield name,url

	def get_moive_url(self,category,urlhead):
		channels = data.get('available_channels')
		for channel in channels.values():
			if channel.get('category_name') == category:
				url = ( urlhead + channel.get('stream_id') + "." + channel.get('container_extension') )

				name = channel.get('name')
				yield name,url

	


def save_in_file(path,ts_iter):	
	with open(path,'w+') as fp:
		fp.write("#EXTM3U\n")
		for (name,url) in ts_iter:
			fp.write("#EXTINF:-1,%s\n" % name)
			fp.write(url + '\n')



if __name__ == '__main__':

	allDic = {}
	live = {}
	movie = {}

	url = ("http://anatoliantv.xyz:7412/panel_api.php?username=fullstreamx1&password=CuFUOiB2xH")
	data = get_json_from_url(url)

	Sall = ALLStream(data)
	
	Sall.get_server_info('url','port')
	Sall.get_user_info('username','password')
	categories_of_live_name = Sall.get_category_of_live()
	categories_of_movie_name = Sall.get_category_of_movie()
	print categories_of_movie_name
	infos = Sall.get_info_without_id()

	urlhead = make_url_head(infos,'live')
	i = 0
	for category in categories_of_live_name:
		ts = {}
		for name,url in Sall.get_live_url(category,urlhead):
#			print name,url
			ts.setdefault(name,url)
			i += 1

		live.setdefault(category,ts)
	print i

	urlhead = make_url_head(infos,'movie')
	for category in categories_of_movie_name:
		mkv = {}
		for name,url in Sall.get_moive_url(category,urlhead):
#			print name,url
			mkv.setdefault(name,url)
			i += 1

		movie.setdefault(category,mkv)
	print i

	allDic.setdefault('live',live)
	allDic.setdefault('movie',movie)
#	print allDic


	
	with open("./all_tv_channels_fullstreamx1.json","w") as fp:
		json.dump(allDic,fp)
