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

class TRStream(object):
	def __init__(self,j_data):
		self.data = j_data
		self.category_id = []
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
	
	def get_category_id(self,rexp):
		lives = self.data.get('categories').get('live')
		for live in lives:
			if live.get('category_name').find(rexp) != -1:
				self.category_id.append(live.get('category_id'))

		return self.category_id

	def get_all_live_url(self,type_id,urlhead):
		channels = data.get('available_channels')
		for channel in channels.values():
			if channel.get('category_id') in self.category_id:
				url = urlhead + channel.get('stream_id') + ".ts"
				name = channel.get('name')
				yield name,url

	

	
	
def save_in_file(path,ts_iter):

	with open(path,'w+') as fp:
		fp.write("#EXTM3U\n")
		for (name,url) in ts_iter:
			fp.write("#EXTINF:-1,%s\n" % name)
			fp.write(url + '\n')



if __name__ == '__main__':
	url = ("http://anatoliantv.xyz:7412/panel_api.php?username=fullstreamx1&password=CuFUOiB2xH")
	data = get_json_from_url(url)

	trs = TRStream(data)
	try:
		trs.get_server_info('url','port')
		trs.get_user_info('username','password')
	except KeyError,e:
		print e

	infos = trs.get_info_without_id()
	ids = trs.get_category_id('TR:')
	urlhead = make_url_head(infos,'live')
	
	ts_iter = trs.get_all_live_url(ids,urlhead)

	save_in_file('./TR_tv_channels_fullstreamx1.m3u',ts_iter)
	

