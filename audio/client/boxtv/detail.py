#!/usr/bin/python
#coding:utf-8

import requests
from bs4 import BeautifulSoup

req = requests.get("http://www.boxtv.com/movies/watch-dhadaka-online")

soup = BeautifulSoup(req.text,"lxml")
print type(soup)
#playerWrapper = soup.select('#playerWrapper')
#playerWrapper = soup.find('section',attrs={'id':'playerWrapper'})
clipDetailBlock = soup.find('section',attrs={'id':'clipDetailBlock'})
print clipDetailBlock,type(clipDetailBlock)
soup = BeautifulSoup(clipDetailBlock)
print clipDetailBlock.hgroup.h1.text
print clipDetailBlock.ul
print clipDetailBlock.ul.next_sibling.next_sibling


print clipDetailBlock.p.text
