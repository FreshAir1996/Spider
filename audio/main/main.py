#!/usr/bin/python
#coding:utf-8
import os
import sys
import ctypes
import subprocess
import datetime
import re 
path_import = os.getcwd().rsplit('/',1)[0]
sys.path.append(path_import)
from allindiasongs import allindiasongs
from indiamp3 import mul_thread  #single #indiamp3
from mysql import mydb

#rule_link = re.compile(r"'(.*?)'")
#clib = ctypes.cdll.LoadLibrary('./libpycall.so')
#clib.init()

def save_to_local(tempfiles):
    start = datetime.datetime.now()
    fNew = open("New.sql","w+")
    fNew.write("Add at " + str(start) + ";\n")
    for temp in tempfiles:
        for string in open(temp):
            fNew.write(string)
#            try:
#                link = re.findall(rule_link,string)[2]
#            except IndexError:
#                continue
#            else:
#                if not lib.get_input_info(link):
#                    fNew.write(string)
        os.remove(temp)

    fNew.close()
    return 0
    


def save_to_database():
    conn = mydb.getHandleforDb("skytv")
    fNew = open("New.sql","r")
    fOld = open("Old.sql","a+")
    fOld.write(fNew.read())
    fNew.seek(0,0)
#    mydb.insert(conn,fNew)

    fNew.close()
    fOld.close()
    return 0


def func0(webs,index):
    names = allindiasongs.main()
    webs[int(index)] += " (Chosen)"
    return names

def func1(webs,index):
    names = mul_thread.main()
    webs[int(index)] += " (Chosen)"
    return names

def whole(webs,index,fs=None,fm=None):
    print "Get resources of all webs"

def func3(webs,index,fs=None,fm=None):
    sys.exit()

def defalut(webs,index):
    print "Your choice inexistent!!"

def chat_with(webs):
    switcher = {'0':func0,'1':func1,'2': whole,'3':func3}
    while True:
        print "Please Choose links(one / all) if you want:\n"
        for i in range(len(webs)):
            print "%d--%s" % (i,webs[i])

        x = raw_input("\nInput your choice:")
        
        func = switcher.get(x)
        switcher[x] = None
        if func:
            names = func(webs,x)
            print "获取资源完成，请选择保存方式:"
            print "1.保存到本地文件  2.保存到数据库"
            x = raw_input("\n请输入保存方式:")
            if x == '1':
                print names
                save_to_local(names)
                print "保存到本地成功\n"
            elif x == '2':
                print names
                save_to_local(names)
                save_to_database()
                print "保存到数据库成功\n"
            else:
                print "您的选择有误\n"
        else :
            print "您的选择有误或已选择过该网页，请重新选择\n"
        
if __name__ == '__main__':
    webs = ["https://www.allindiasongs.com(Mp3)","https://www.indiamp3.com/(Mp3)","All","Exit"]

    chat_with(webs) 

