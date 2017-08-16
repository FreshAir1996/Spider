#!/usr/bin/python
#coding:utf-8
import os
import sys
import re 
path_import = os.getcwd().rsplit('/',1)[0]
print path_import
sys.path.append(path_import)
from indiamp3 import indiamp3


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
    indiamp3.main()
    webs[int(index)] += " (Chosen)"
    return 0


def whole(webs,index,fs=None,fm=None):
    print "Get resources of all webs"

def func3(webs,index,fs=None,fm=None):
    sys.exit()

def defalut(webs,index):
    print "Your choice inexistent!!"

def chat_with(webs):
    switcher = {'0':func0,'1': whole,'2':func3}
    while True:
        print "Please Choose links(one / all) if you want:\n"
        for i in range(len(webs)):
            print "%d--%s" % (i,webs[i])

        x = raw_input("\nInput your choice:")
        
        func = switcher.get(x)
#        switcher[x] = None
        if func:
            func(webs,x)
        else :
            print "您的选择有误或已选择过该网页，请重新选择\n"
        
if __name__ == '__main__':
    webs = ["https://www.indiamp3.com/(Mp3)","All","Exit"]

    chat_with(webs) 

