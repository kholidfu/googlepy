#!/usr/bin/env python

import gevent
from gevent import monkey
monkey.patch_all()
import urllib2

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
    print '%s: %s bytes: %r' % (url, len(html), html[:50])

jobs = [gevent.spawn(grab, url) for url in urls]
gevent.joinall(jobs)
