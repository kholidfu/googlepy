#!/usr/bin/env python

import urllib2

def test():
    url = "https://www.google.com/search?q=toyota+owners+manual+filetype:pdf&oq=search+google+100+results&num=100"
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    html = opener.open(url).read()
    return html

print test()
