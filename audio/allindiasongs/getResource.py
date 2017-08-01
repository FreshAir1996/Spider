#!/usr/bin/python
#coding:utf-8

"""
    This module's name means function. We can get the resources in its
    function from "https://www.allindiasongs.com/".
    Example:getLi ---> get all list of webs
"""
import re
import subprocess
import sys
import os
import time
import datetime
import multiprocessing as mul
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding("utf-8")



def getLi(text):            
    rule_li = r'<li\s><a\shref="(.*?)"'
    re_li = re.compile(rule_li,re.M)
    for string in open(text):
        htmllist = re.findall(re_li,string)
        if htmllist:
            return htmllist

def getTitle(text):
    rule_title = r'<h1 class="entry-title">(.*?)</h1>'
    re_title = re.compile(rule_title)
    for string in open(text):
        title = re.findall(re_title,string)
        if title:
            return title[0]

def getImg(text):
    rule_img = r'src="(.*?\.jpg).*?"'
    re_img = re.compile(rule_img)
    for string in open(text):
        image = re.findall(re_img,string)
        if image:
            return image[0]
    return 

def getMp3(text):
    rule_mp3 = r'<a href="(.*?\.mp3)"'
    re_mp3 = re.compile(rule_mp3)
    mp3_list = []
    for string in open(text):
        mp3 = re.findall(re_mp3,string)
        if mp3:
            mp3_list.append(mp3[0])
    return mp3_list

def getMp3Name(string):
    name = string.split('/')[-1].split('-')[-1].split('%5b')[-2].replace('%20',' ').strip()
    return name

# download the html
def getTextByCurl(url):
    name = url.split('/')[-2]
    child = subprocess.Popen(['curl','-o',name,url])
    child.communicate()


def insertIntoSpecial(TextOfHtml,cur):
    tempstring = ''
    sql = "select * from special where name='%s'" % (getTitle(TextOfHtml))

    if cur.execute(sql):
	print 'SQL'
        pass
    else:

        try:
            html_file = open(TextOfHtml)
            soup = BeautifulSoup(html_file,"html.parser")
            tempfile = str(soup.select(".entry-content"))
            soup = BeautifulSoup(tempfile,"html.parser")

            rule = r'[Mm]usic'
            re_cast = re.compile(rule)

            for string in soup.select("p"):
                result = re.findall(re_cast,string.text)
                if result:
    #                data.append(string.text)
                    tempstring += ("('%s','%s','%s'),\n" %
            (getTitle(TextOfHtml),getImg(TextOfHtml),string.text.decode("raw_unicode_escape")))
#    		    time.sleep(1)
#    		    print "Special"
                    break
        except Exception as e:
            print e
    
    return tempstring
  
 

def insertIntoMusic(TextOfHtml,cur,lib):
    
    tempstring = ''
    mp3list =  getMp3(TextOfHtml)
    for mp3 in mp3list:
        try:
            name = getMp3Name(mp3)
	    title = getTitle(TextOfHtml)
#            print name
	except IndexError as e:
	    print e
        except KeyboardInterrupt:
	    sys.exit()
	else:
            sql =( "select * from music where name='%s' and album='%s'" % (name,title))
            try:
                if cur.execute(sql):
                    pass
                else :
	    	    if not lib.get_input_info(mp3):
    	            	print "Music"
                    	tempstring += ("('%s','%s','%s'),\n" % (getMp3Name(mp3),getTitle(TextOfHtml),mp3 ))
	    except Exception as e:
		pass
#            os.exit()
#	    print 'hello'
#            else:
   

    
    return tempstring
    


if __name__ == '__main__':

 href="http://www.atozmp3.lol/1/2016/Sri-Sri/320/01%20-%20Enni%20Janmala%20Bandhamo%20%5Bwww.AtoZmp3.in%5D.mp3"
 print getMp3Name(href)  
    
