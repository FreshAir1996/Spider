#!/usr/bin/python
#coding:utf-8
import sys
import ctypes
import MySQLdb
import datetime
import warnings
import multiprocessing as mul
from getResource import get_links_for_album,get_list_for_web,getInfoQuickly

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

   
#获得数据库需要的全部信息
def save_info(list_album,fp):
	conn = getHandleforDb("skytv")
	cur = conn.cursor()
	i = 1
	for link in get_links_for_album(list_album):
		print "Get album from (%s,%d)" % (list_album,i)
		resources = getInfoQuickly(link['href'],cur)
		if len(resources):
			resources = resources[:-2] + ";" + resources[-1:]
			try:
				sql = "insert into test values \n%s" % resources
				cur.execute(sql)
			except Exception as e:
				print "Save failed as %s" % e
			else:
				fp.write(sql)

		i += 1
	cur.close()
	conn.close()
	fp.close()
	
def main_process():
    
    Start = datetime.datetime.now()
    urls = get_list_for_web("all.html")
    names = ["./.log/" +(urls[x].rsplit("/",1)[-1])  for x in range(27)]

    f0 = open(str(names[0]),"w+")
    fa = open(str(names[1]),"w+")
    fb = open(str(names[2]),"w+")

    f0_process = mul.Process(target=signal,args=(url[0],f0,clib))
    fa_process = mul.Process(target=signal,args=(url[1],fa,clib))
    fb_process = mul.Process(target=signal,args=(url[2],fb,clib))

    f0_process.start()
    fa_process.start()
    fb_process.start()

    f0_process.join()
    fa_process.join()
    fb_process.join()

    End = datetime.datetime.now()

    print "Start at : " , Start
    print "End at : " , End
    return names

def ttt():
    
    Start = datetime.datetime.now()
    urls = get_list_for_web("indiamp3.html")
    names = ["./.log/X.sql","./.log/Q.sql"]
   
    fx = open(str(names[0]),"w+")
    fq = open(str(names[1]),"w+")

    fx_process = mul.Process(target=save_info,args=(urls[24],fx))
    fq_process = mul.Process(target=save_info,args=(urls[17],fq))

    fx_process.start()
    fq_process.start()

    fx_process.join()
    fq_process.join()
    
    End = datetime.datetime.now()

    return names



if __name__ == '__main__':

    ttt()

