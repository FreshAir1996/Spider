#!/usr/bin/python
import sys
import ctypes
import MySQLdb
import datetime
import threading 
import multiprocessing as mul
from getResource import get_list_for_album,get_links_for_album,get_single_album


clib = ctypes.cdll.LoadLibrary('./libpycall.so')
clib.init()

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

   
def signal(url,fp,clib):
    conn = getHandleforDb("skytv")
    cur = conn.cursor()
    for link in get_links_for_album(url):
        resources = get_single_album(link['href'],cur,clib)
	if len(resources):
	    fp.write("insert into music values\n" +resources)
            fp.seek(-2,2)
            fp.write(";\n")
    fp.close()	
    cur.close()		
    conn.close()
   

def pool_to_do(url):
    path = "./.log/" + url.rsplit("/",1)[-1]
    f = open(path,"w+")
    signal(url,f,clib)	
    return path

def ttt():
    try:
    	Start = datetime.datetime.now()
    	clib = ctypes.cdll.LoadLibrary('./libpycall.so')
    	clib.init()
   	urls = get_list_for_album("all.html")
#    print urls
    	p = mul.Pool(3)
    	p.map(pool_to_do,urls)
    	p.close()
    	p.join()
    except KeyboardInterrupt:
	sys.exit()

    print "hello"
    return names

def main_thread():
    
    Start = datetime.datetime.now()
    clib = ctypes.cdll.LoadLibrary('./libpycall.so')
    clib.init()
    names=['./.log/0-9.txt','./.log/A.txt','./.log/B.txt']
    url =['https://www.indiamp3.com/list/0-9','https://www.indiamp3.com/list/A','https://www.indiamp3.com/list/B']
    
    f0 = open(names[0],"w+")
    fa = open(names[1],"w+")
    fb = open(names[2],"w+")
#    try:
    f0_thread = threading.Thread(target=signal,args=(url[0],f0,clib))
    fa_thread = threading.Thread(target=signal,args=(url[1],fa,clib))
    fb_thread = threading.Thread(target=signal,args=(url[2],fb,clib))

    f0_thread.start()
    fa_thread.start()
    fb_thread.start()
    f0_thread.join()
    fa_thread.join()
    fb_thread.join()

#    except KeyboardInterrupt:
#	sys.exit()

    End = datetime.datetime.now()


if __name__ == '__main__':

    ttt()
#    action = pool_to_do("https://www.indiamp3.com/list/0-9")
#    action("https://www.indiamp3.com/list/0-9")
