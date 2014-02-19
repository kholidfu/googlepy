import urllib2
from bs4 import BeautifulSoup
import pymongo
import time

c = pymongo.Connection()
db = c['terms']
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# ebookbrowse
while True:
    try:
        html = opener.open("http://ebookbrowsee.net/").read()
        soup = BeautifulSoup(html)
        div = soup.find('div', attrs={'class': 'rel_search'})
        for d in div.findAll('a'):
            if db.term.find_one({'term': d.getText()}) is None:
                db.term.insert({
                    'term': d.getText(),
                    'status': 0,
                    'type': 'pdf',
                    })
    except:
        print 'something error happened! wait for 30 seconds ...'
        time.sleep(30)
        continue

    time.sleep(5)
