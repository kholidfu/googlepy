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

# database thing
c = pymongo.Connection()
pdfdb = c['pdfs']
termsdb = c['terms']

# termsdb schema
# {'term': 'theterm', 'status': 0} keyword not used
# {'term': 'theterm', 'status': 1} keyword already used
# get 10/100 random terms which status is 0
# for i in chosen keywords
_len = termsdb.term.find().count()
keywords = [i['term'] for i in termsdb.term.find({'status': 0}).skip(randint(0, _len - 10)).limit(10)]
# update status from 0 to 1
for key in keywords:
    termsdb.term.update({'term': key}, {"$set": {'status': 1}})

print 'keywords loaded, ready to launch the machine...'

google_urls = ["https://www.google.com/search?q=" + key.replace(' ', '+') + "+filetype:pdf&num=100" for key in keywords]

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
gevent.joinall(jobs)
results = [job.value for job in jobs]

## keywords
keys = keywords

# google suggest
def gsuggest(key):
    url = "http://google.com/complete/search?output=toolbar&q=" + key.replace(' ', '+')
    google_suggest = urllib2.urlopen(url)
    suggests = etree.parse(google_suggest)
    google_suggest_data = []
    for suggest in suggests.iter('suggestion'):
        google_suggest_data.append(suggest.get('data'))
    return google_suggest_data

jobs = [gevent.spawn(gsuggest, key) for key in keys]
gevent.joinall(jobs)
google_suggest_data = [job.value for job in jobs]

# bing suggest
def bsuggest(key):
    url = "http://api.bing.com/osjson.aspx?query=" + key.replace(' ', '+')
    bing_suggest = urllib2.urlopen(url).read()
    bing_suggest_data = bing_suggest.replace('[', '').replace(']', '').replace('"', '')
    bing_suggest_data = bing_suggest_data.split(',')[1:]
    return bing_suggest_data

jobs = [gevent.spawn(bsuggest, key) for key in keys]
gevent.joinall(jobs)
bing_suggest_data = [job.value for job in jobs]

for i in range(len(results)): # jumlah (len) sesuai jumlah (len) keywords ex: 10
    for r in results[i]: # jumlah (len) sesuai parameter num= ex: 100
        r.update({'keyword': keys[i]})
        r.update({'google_suggests': google_suggest_data[i]})
        r.update({'bing_suggests': bing_suggest_data[i]})
        pdfdb.pdf.insert(r)

# sample data
# [{u'_id': ObjectId('52cbb9ffdde3685e2057738b'),
#   u'bing_suggests': [u'grammar for ielts download',
#                      u'grammar for ielts',
#                      u'grammar for ielts pdf',
#                      u'grammar for ielts free download',
#                      u'grammar for ielts with answers download',
#                      u'grammar for ielts book',
#                      u'grammar for ielts.pdf',
#                      u'grammar for ielts cambridge',
#                      u'grammar for ielts.pdf all pages'],
#   u'google_suggests': [u'grammar for ielts',
#                        u'grammar for ielts pdf',
#                        u'grammar for ielts free download',
#                        u'grammar for ielts cambridge',
#                        u'grammar for ielts with answers',
#                        u'grammar for ielts download',
#                        u'grammar for ielts cd',
#                        u'grammar for ielts ebook',
#                        u'grammar for ielts audio',
#                        u'grammar for ielts book'],
#   u'keyword': u'grammar for ielts',
#   u'snippet': u'F2-IELTS Refund of Deposit Results Form 2012-13 (120817).doc. Hong Kong \nBaptist University ... Activate Your Spoken Grammar for IELTS. P.T.O &. Form 2\xa0...',
#   u'title': u'Hong Kong Baptist University Language Centre IELTS Results Form',
#   u'url': u'http://lc.hkbu.edu.hk/english/ielts/download/ielts_results_form.pdf'}]
