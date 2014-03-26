#!/usr/bin/env python
import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import re
import pymongo
from random import randint
import xml.etree.ElementTree as etree
from urllib import unquote
from unidecode import unidecode
from datetime import datetime

# database thing
c = pymongo.Connection()
pdfdb = c['pdfs']
termsdb = c['terms']
gsuggestsdb = c['gsuggests']
bsuggestsdb = c['bsuggests']

# termsdb schema
# {'term': 'theterm', 'status': 0} keyword not used
# {'term': 'theterm', 'status': 1} keyword already used
# get 10/100 random terms which status is 0
# for i in chosen keywords
_len = termsdb.term.find().count()
keywords = [{'term': unidecode(i['term']), 'type': i['type']} \
            for i in termsdb.term.find({'status': 0}).\
            skip(randint(0, _len - 10)).\
            limit(10)]
# update status from 0 to 1
for key in keywords:
    termsdb.term.update({'term': key['term']}, {"$set": {'status': 1}})

print 'keywords loaded, ready to launch the machine...'

google_urls = ["https://www.google.com/search?q=" \
               + key['term'].replace(' ', '+') \
               + "+filetype:" + key['type'] + "&num=100" for key in keywords]

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
    ahrefs = [i.find('a')['href'] for i in soup.findAll('h3',
                                                        attrs={'class': 'r'})]
    pattern = re.compile(r"=(.*?)&")
    urls = [re.search(pattern, i).group(1) for i in ahrefs]
    ## prevent from string quoting on url
    urls = [unquote(url) for url in urls]
    ## get snippet
    snippets = [i.get_text() for i in soup.findAll('span',
                                                   attrs={'class': 'st'})]
    ## gathering data
    container = []
    ## format data
    if len(titles) == len(urls) == len(snippets):
        for i in range(len(titles)):
            container.append({'title': titles[i], 'url': urls[i],
                              'snippet': snippets[i]})
    return container

# join all jobs
jobs = [gevent.spawn(grab, url) for url in google_urls]
print 'starting to crawl...'
gevent.joinall(jobs)
results = [job.value for job in jobs]

## keywords
keys = keywords

# google suggest
def gsuggest(key):
    url = "http://google.com/complete/search?output=toolbar&q=" \
      + key.replace(' ', '+')
    google_suggest = urllib2.urlopen(url)
    suggests = etree.parse(google_suggest)
    #google_suggest_data = []
    for suggest in suggests.iter('suggestion'):
        # upsert > mongo
        try:
            #gsuggestsdb.suggest.insert({'word': unidecode(unicode(suggest.get('data')))})
            gsuggestsdb.suggest.update({'word': unidecode(unicode(suggest.get('data')))}, {'word': unidecode(unicode(suggest.get('data')))}, upsert=True)
        except:
            continue

jobs = [gevent.spawn(gsuggest, key['term']) for key in keys]
gevent.joinall(jobs)
#google_suggest_data = [job.value for job in jobs]

# bing suggest
def bsuggest(key):
    url = "http://api.bing.com/osjson.aspx?query=" + key.replace(' ', '+')
    bing_suggest = urllib2.urlopen(url).read()
    bing_suggest_data = bing_suggest.replace('[', '').replace(']', '').\
      replace('"', '')
    bing_suggest_data = bing_suggest_data.split(',')[1:]
    #return bing_suggest_data
    for bing in bing_suggest_data:
        # upsert > mongo
        try:
            #bsuggestsdb.suggest.insert({'word': unidecode(unicode(bing))})
            bsuggestsdb.suggest.update({'word': unidecode(unicode(bing))}, {'word': unidecode(unicode(bing))}, upsert=True)
        except:
            continue

jobs = [gevent.spawn(bsuggest, key['term']) for key in keys]
gevent.joinall(jobs)
#bing_suggest_data = [job.value for job in jobs]

"""
data pdf ex:
{title: 'thetitle', url: 'theurl', snippet: 'thesnippet', keyword: 'thekwyrod'}
data gsuggests ex:
{word: 'theword'}
data bsuggests ex:
{word: 'theword'}
"""

for i in range(len(results)): # jumlah (len) sesuai jumlah (len) keywords ex: 10
    for r in results[i]: # jumlah (len) sesuai parameter num= ex: 100
        r.update({'keyword': keys[i]['term']})
        r.update({'added': datetime.now()})
        pdfdb.pdf.insert(r)
