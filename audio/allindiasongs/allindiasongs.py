#coding:utf-8
import getResource
import os
import sys
import ctypes
import datetime
import multiprocessing as mul
import MySQLdb 

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

'''
Test .................

def get_temp_file(function,f,cur):
    
    pwd = os.getcwd()
    start = datetime.datetime.now()
    f.write("Add at " + str(start) + ";\n")
	
    os.chdir('./htmlfiles/')
    files = os.listdir('./')
    for html in files:
        function(html,f,cur)

    os.chdir(pwd)
    f.seek(-2,2)
    f.write(";\n")
    f.close()
'''
def main_special(files,fs):
    conn = getHandleforDb("skytv")
    cur = conn.cursor()
    fs.write("insert into special values\n")
    for html in files:
        resources = getResource.insertIntoSpecial(html,cur)
	if len(resources):
	    fs.write(resources)

    fs.seek(-2,2)
    fs.write(";\n")
    fs.close()

def main_music(files,fm,clib):
    conn = getHandleforDb("skytv")
    cur = conn.cursor()
    for html in files:
        resources = getResource.insertIntoMusic(html,cur,clib)
	if len(resources):
	    fm.write("insert into music values\n" + resources)
	    fm.seek(-2,2)
	    fm.write(";\n")
    fm.close()

def main():
#    print pwd
    start = datetime.datetime.now()
    clib = ctypes.cdll.LoadLibrary('./libpycall.so')
    clib.init()
    pwd  = os.getcwd()

    names = ["./.log/.special_allindia","./.log/.music_allindia"]
    fs = open(names[0],"w")
    fm = open(names[1],"w")
    os.chdir('../htmlfiles/')
    files = os.listdir('./')

    special_process = mul.Process(target=main_special,args=(files,fs,))
    music_process =  mul.Process(target=main_music,args=(files,fm,clib))

    special_process.start()
    music_process.start()

    special_process.join()
    music_process.join()
    os.chdir(pwd)
    end = datetime.datetime.now()

    print "All insert start at : " , start
    print "All insert end at : ", end

    return names

if __name__ =='__main__':
    
    main()
