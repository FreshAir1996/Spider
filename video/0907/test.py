#!/usr/bin/python
#coding:utf-8
from urllib2 import urlopen
import json


with open("./all_tv_channels_fullstreamx1.json","r") as fp:
	dic = json.load(fp)
def save_in_file(path,dic):	
	i = 0
	with open(path,'w+') as fp:
		fp.write("#EXTM3U\n")
		for value in dic['live'].values():
			for name,url in value.items():
				fp.write("#EXTINF:-1,%s\n" % name.encode('utf8'))
				fp.write(url.encode('utf8') + '\n')
				i += 1
		for value in dic['movie'].values():
			for name,url in value.items():
				
				fp.write("#EXTINF:-1,%s\n" % name.encode('utf8'))
				fp.write(url.encode('utf8') + '\n')
				
				i += 1
	print i


save_in_file("./TR_tv_channels_fullstreamx1.m3u",dic)

