#!/usr/bin/env python
import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import re
import pymongo
from urllib import unquote
from datetime import datetime
from unidecode import unidecode
from random import randint


# database thing
c = pymongo.Connection()
mediadb = c['files']
termsdb = c['terms']

# termsdb.nonpdfterm.find()
_len = termsdb.nonpdfterm.find().count()
keywords = [{'keyword': unidecode(i['keyword']), 'type': i['type'], 'source': i['source'], 'source_url': i['source_url']} for i in termsdb.nonpdfterm.find({'status': 0}).skip(randint(0, _len - 10)).limit(1)]

# update status from 0 to 1
for key in keywords:
    termsdb.nonpdfterm.update({'keyword': key['keyword']}, {"$set": {'status': 1}})

# terms = {
#     'keyword': 'crack xbox mediafire.com',
#     'type': 'rar',
#     'source': 'pastebin',
#     'source_url': 'pastebin.com',
#     'status': 0,
#     }

google_urls = ["https://www.google.com/search?q=" + keyword['keyword'].replace(' ', '+') + "+" + keyword['type'] + "+\"" + keyword['source_url'] + "\"" + "&num=10" for keyword in keywords]

def grab(url):
    print 'Starting %s' % url
    # http request
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    html = opener.open(url).read()
    # soup coming in
    soup = BeautifulSoup(html)
    # parsing
    ## get title
    titles = [i.get_text() for i in soup.findAll('h3', attrs={'class': 'r'})]
    ## get url
    ahrefs = [i.find('a')['href'] for i in soup.findAll('h3', attrs={'class': 'r'})]
    pattern = re.compile(r"=(.*?)&")
    urls = [re.search(pattern, i).group(1) for i in ahrefs]
    ## prevent from string quoting on url
    urls = [unquote(url) for url in urls]
    ## get snippet
    snippets = [i.get_text() for i in soup.findAll('span', attrs={'class': 'st'})]
    ## gathering data
    container = []
    ## format data
    if len(titles) == len(urls) == len(snippets):
        for i in range(len(titles)):
            container.append({'title': titles[i], 'url': urls[i], 'snippet': snippets[i]})
    return container

# join all jobs
jobs = [gevent.spawn(grab, url) for url in google_urls]
print 'starting to crawl...'
gevent.joinall(jobs)
results = [job.value for job in jobs]


for i in range(len(results)): # jumlah (len) sesuai jumlah (len) keywords ex: 10
    for r in results[i]: # jumlah (len) sesuai parameter num= ex: 100
        r.update({'keyword': keywords[i]['keyword']})
        r.update({'type': keywords[i]['type']})
        r.update({'source': keywords[i]['source']})
        r.update({'source_url': keywords[i]['source_url']})
        r.update({'crawl': 0})
        r.update({'added': datetime.now()})
        mediadb.nonpdf.insert(r)
