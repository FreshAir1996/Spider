#!/usr/bin/python
#coding:utf-8

import os
import sys
import FFmpeg
import mylogger

reload(sys)
sys.setdefaultencoding('utf-8')

FFmpeg.init()
#FFmpeg.setTimeout(100)
def getStatusOfStream(text,log):

	with open(text) as fp:
		fp.next()
		while True:
			
			try:
				tv_name = fp.next().split(',')[-1].strip()
				tv_url = fp.next().strip()
				#do something
				errno = FFmpeg.getLiveStatus(tv_url)
				if errno:
					reason = FFmpeg.err2str(errno)
#					print tv_name,tv_url,reason
					log.error("%s (%s) : %s" % (tv_name,tv_url,reason))
				else:
					print  "Is Arrived"
			except StopIteration:
				fp.close()
				break



if __name__ == '__main__':
	input = raw_input("Please Input Your Choose (1.ts 2.rtmp)")
	if input == '1':
		os.system(": > live_ts.log")
		log = mylogger.Logger('live_ts.log')
		getStatusOfStream('./TR_tv_channels_fullstreamx1.m3u',log)
	else:
		os.system(": > live_rtmp.log")
		log = mylogger.Logger('live_rtmp.log')
		getStatusOfStream('./rtmp_fullstreamx1.m3u',log)

