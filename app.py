#!/usr/bin/env python

import gevent
from gevent import monkey
monkey.patch_all()

import urllib2
from bs4 import BeautifulSoup
import re

keywords = [
'toyota owners manual',
'honda owners manual',
'mitsubishi owners manual',
'suzuki owners manual',
'nikon owners manual',
'canon owners manual',
'python ebook',
'php ebook',
'ruby on rails tutorial',
'java ebook tutorial'
        ]

urls = ["https://www.google.com/search?q=" + keyword.replace(' ', '+') + "+filetype:pdf&oq=search+google+100+results&num=100" for keyword in keywords]

def grab(url):
    print 'Starting %s' % url
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    html = opener.open(url).read()
    #print '%s: %s bytes: %r' % (url, len(html), html[:50])
    # soup coming in
    soup = BeautifulSoup(html)
    # parsing
    titles = [i.get_text() for i in soup.findAll('h3', attrs={'class': 'r'})]
    ahrefs = [i.find('a')['href'] for i in soup.findAll('h3', attrs={'class': 'r'})]
    pattern = re.compile(r"=(.*?)&")
    #re.search(re.compile(r"q=(.*?)&"), u).group(1)
    urls = [re.search(pattern, i).group(1) for i in ahrefs]
    snippets = [i.get_text() for i in soup.findAll('span', attrs={'class': 'st'})]
    print titles[0]
    print urls[0]
    print snippets[0]
    print '='
    print

jobs = [gevent.spawn(grab, url) for url in urls]
gevent.joinall(jobs)
