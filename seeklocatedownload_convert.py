import urllib
import urllib2
import csv
#from bs4 import BeautifulSoup
import sys
import subprocess
import os.path

TRACKLIST =  sys.argv[1]

with open(TRACKLIST, "rb") as f:
    #f2 = open('2_listWithUrl.csv','w')
    reader = csv.reader(f, delimiter="|")
    for i, line in enumerate(reader):
        print line[0] + ' - ' + line[1] + ' - ' + line[2]
        if os.path.isfile('artbuffer/' + line[0] + '.jpg'):
            mp3Art = 'artbuffer/' + line[0] + '.jpg'
        else:
            mp3Art = 'mystery.jpg'
        #print subprocess.Popen("echo " + line[0] + " - " + line[1] + " - " + line[2] + " >> test.csv", shell=True, stdout=subprocess.PIPE).stdout.read()
        if os.path.isfile('filebuffer/' + line[0] + '.mp3'):

            print subprocess.Popen("ffmpeg -hide_banner -nostats -loglevel error -i \'filebuffer/" + line[0] + ".mp3\' -vn -ab 192k -ar 44100 -y \'tmp.mp3\' ", shell=True, stdout=subprocess.PIPE).stdout.read()


            print subprocess.Popen("ffmpeg -hide_banner -nostats -loglevel error -i \'tmp.mp3\' -i \'" + mp3Art + "\' -c copy -map 0 -map 1 -metadata:s:v title='Cover (front)' -metadata title=\'" + line[2] + "\' -metadata ARTIST=\'" + line[1] + "\' -metadata publisher=\'" + line[3] + "\' -y \'output/" + line[1] + " - " + line[2] + ".mp3\' ", shell=True, stdout=subprocess.PIPE).stdout.read()
        else:
            f2 = open('convert_error.log','w')
            f2.write( line[0] + ' - ' + line[1] + ' - ' + line[2] + ' - File not downloaded') 