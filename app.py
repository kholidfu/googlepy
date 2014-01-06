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

keywords = ['toyota owners manual', 'honda owners manual', 'suzuki owners manual', 'mistubishi owners manual']
google_urls = ["https://www.google.com/search?q=" + keyword.replace(' ', '+') + "+filetype:pdf&oq=search+google+100+results&num=5" for keyword in keywords]

def grab(url):
    print 'Starting %s' % url
    # http request
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    html = opener.open(url).read()

    # soup coming in
    soup = BeautifulSoup(html)

    # parsing
    ## keywords
    keys = keywords

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
            container.append({'title': titles[i], 'url': urls[i], 'snippets': snippets[i]})

    return container

# join all jobs
jobs = [gevent.spawn(grab, url) for url in google_urls]
gevent.joinall(jobs)

# finishing touch
results = [job.value for job in jobs]
data = {}
for i in range(len(results)):
    # insert into mongodb
    db.pdf.insert({'keyword': keywords[i], 'results': results[i]})
