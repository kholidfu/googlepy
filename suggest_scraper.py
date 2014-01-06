import urllib2
import xml.etree.ElementTree as etree

xml = urllib2.urlopen("http://google.com/complete/search?output=toolbar&q=toyota+owners+manual")

data = etree.parse(xml)

for d in data.iter('suggestion'):
    print d.get('data')
