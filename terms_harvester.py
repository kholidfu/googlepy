import urllib2
from bs4 import BeautifulSoup

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# ebookbrowse
html = opener.open("http://ebookbrowsee.net/").read()
soup = BeautifulSoup(html)

div = soup.find('div', attrs={'class': 'rel_search'})
for d in div.findAll('a'):
    print d.getText()

# format dbase
# {'term': 'theterm', 'status': 0} # not inserted yet
# {'term': 'theterm', 'status': 1} # inserted
