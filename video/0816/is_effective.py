#!/usr/bin/python
#coding:utf-8

import FFmpeg
import mylogger

FFmpeg.init()

def getStatusOfTv(text,log):

	with open(text) as fp:
		
		while True:
			
			try:
				tv_name = fp.next().split(',')[-1].strip()
				tv_url = fp.next().strip()
				#do something
				errno = FFmpeg.getLiveStatus(tv_url)
				if errno:
					reason = FFmpeg.err2str(errno)
					print tv_name,tv_url,reason
					log.error("%s -- (%s)" % (tv_name,tv_url))
				else:
					print  "Is Arrived"
			except StopIteration:
				fp.close()
				break



if __name__ == '__main__':
	log = mylogger.Logger('live.log')
	getStatusOfTv('./usetvlist.m3u',log)
