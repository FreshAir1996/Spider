#!/usr/bin/python
#coding:utf-8

import requests
from bs4 import BeautifulSoup

req =  requests.get("http://www.boxtv.com")
soup = BeautifulSoup(req.text,"lxml")

thumbs = soup.select('.languageThumbs  li a')
print thumbs

#print type(thems[0])
#print req.text

for thumb in thumbs:
	print thumb['href'],thumb.text
