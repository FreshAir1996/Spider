#!/usr/bin/python
#coding:utf-8

import logging,os

class Logger():
	def __init__(self,path,clevel = logging.DEBUG ,flevel = logging.DEBUG):
		self.logger = logging.getLogger(path)
		self.logger.setLevel(logging.DEBUG)

		fmt = logging.Formatter('\nTime:%(asctime)s;\n%(levelname)s:%(message)s\n','%Y-%m-%d %H:%M:%S')
		
		self.sh = logging.StreamHandler()
		self.sh.setFormatter(fmt)
		self.sh.setLevel(clevel)
		
		self.fh = logging.FileHandler(path)
		self.fh.setFormatter(fmt)
		self.fh.setLevel(flevel)

		self.logger.addHandler(self.sh)
		self.logger.addHandler(self.fh)

	def debug(self,message):
		return self.logger.debug(message)

	def info(self,message):
		return self.logger.info(message)

	def warn(self,message):
		return self.logger.warning(message)

	def error(self,message):
		return self.logger.error(message)

	def critical(self,message):
		return self.logger.critical(message)

	def exception(self,message):
		return self.logger.exception(message)

	def setStreamFmt(self,fmt):
		self.sh.setFormatter(fmt)
		self.logger.addHandler(self.sh)

	def setFileFmt(self,fmt):
		self.fh.setFormatter(fmt)
		self.logger.addHandler(self.fh)


def test():
	mylogger = Logger('example.log',logging.WARNING,logging.WARNING)
	mylogger.info("I am an Class")
	fmt = logging.Formatter('Time:%(asctime)s;\nFile:%(pathname)s-->line(%(lineno)s)\n%(levelname)s:\n%(message)s\n','%Y-%m-%d %H:%M:%S')
	mylogger.setStreamFmt(fmt)

	mylogger.warn('Hello World')

if __name__ == '__main__':
	
	mylogger = Logger('example.log',logging.DEBUG,logging.WARNING)

	l = [1,2,3,4,5]

	try:
		print l[20]
	except:
		mylogger.exception('')

	test()       #打开相同名字，还是同一个文件
