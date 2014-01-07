#!/usr/bin/env python
import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import re
import pymongo

# database thing
c = pymongo.Connection()
db = c['pdfs']

keywords = [
    'toyota owners manual',
    'honda owners manual',
    'suzuki owners manual',
    'mitsubishi owners manual',
    'yamaha owners manual',
    'kawasaki owners manual',
    'mazda owners manual',
    'opel owners manual',
    'canon owners manual',
    'nikon owners manual',
    ]

google_urls = ["https://www.google.com/search?q=" + keyword.replace(' ', '+') + "+filetype:pdf&num=100" for keyword in keywords]

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

# finishing touch
results = [job.value for job in jobs]

#for i in range(len(results)):
    # insert into mongodb
    # db.pdf.insert({'keyword': keywords[i], 'results': results[i]})

# atau dimasukkan tiap result
## keywords
keys = keywords

# google suggest
import urllib2
import xml.etree.ElementTree as etree

google_suggest = urllib2.urlopen("http://google.com/complete/search?output=toolbar&q=toyota+owners+manual")
suggests = etree.parse(google_suggest)
google_suggest_data = []
for suggest in suggests.iter('suggestion'):
    google_suggest_data.append(suggest.get('data'))

# bing suggest
url = "http://api.bing.com/osjson.aspx?query=python+programming"
bing_suggest = urllib2.urlopen(url).read()
bing_suggest_data = bing_suggest.replace('[', '').replace(']', '').replace('"', '').split(',')[1:]

for i in range(len(results)):
    for r in results[i]:
        r.update({'keyword': keys[i]})
        r.update({'google_suggests': google_suggest_data})
        r.update({'bing_suggests': bing_suggest_data})
        #print r
        db.pdf.insert(r)
