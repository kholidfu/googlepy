import urllib2

url = "http://api.bing.com/osjson.aspx?query=python+programming"
data = urllib2.urlopen(url).read()
datas = data.replace('[', '').replace(']', '').replace('"', '').split(',')[1:]

print datas
