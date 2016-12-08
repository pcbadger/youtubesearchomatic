import urllib
import urllib2
import csv
from bs4 import BeautifulSoup
import sys
TRACKLIST =  sys.argv[1]

with open(TRACKLIST, "rb") as f:
    f2 = open('getUrlListOutputBuffer.csv','w')
    reader = csv.reader(f, delimiter="\t")
    for i, line in enumerate(reader):

        textToSearch = '{}'.format(line)
        query = urllib.quote(textToSearch)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        regex = ur""
        for vid in soup.findAll(regex, attrs={'class':'yt-uix-tile-link'})[:1]:
            strLine = str(line)
            f2.write(strLine + '|https://www.youtube.com' + vid['href'] + '\n')
            print strLine + ' - https://www.youtube.com' + vid['href']
