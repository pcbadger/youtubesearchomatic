
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import getopt
import urllib
import urllib2
import csv
from bs4 import BeautifulSoup
from urllib2 import Request, urlopen, URLError, HTTPError
import sys
import subprocess
import os.path
import shutil
import re
import string
import requests
import time
import youtube_dl
import eyed3

reload(sys)
sys.setdefaultencoding('utf8')

def checkOptions(argv):
    global REV

    ARTIST = None
    TITLE = None

    try:
        opts, args = getopt.gnu_getopt(argv,"hru:o:a:t:f:",["artist=","title="])
    except gnu_getopt.GetoptError:
        print 'seeker.py -a <ARTIST> -t <TITLE> (you don\'t have to have both)'
        print 'OR' 
        print 'seeker.py -f <FILE>'
        print 'Extras:'
        print '     -r (to reverse title/artist in CSV)'
        print '     -o <OUTPUT DIRECTORY>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -a <ARTIST> -t <TITLE> -f <FILE>'
            sys.exit()
        elif opt in ("-t", "--title"):
            TITLE = arg
            TITLE = reformat(TITLE)
        elif opt in ("-a", "--artist"):
            ARTIST = arg
            ARTIST = reformat(ARTIST)
        elif opt in ("-r", "--rev"):
            REV = "Yo!"
        elif opt in ("-o", "--output"):
            outputDir = arg
            makeTheDir(outputDir)
        elif opt in ("-u", "--url"):
            arg = getTitleFromUrlRetry(arg)
            processTrack(arg)
        elif opt in ("-f", "--file"):
            FILE = arg
            if os.path.isfile(FILE):
                processCSV(arg)
            else:
                print 'No such file!'
                sys.exit()
    

    if ARTIST is not None or TITLE is not None:
        getQuery(TITLE,ARTIST)

def reformat(STUFF):
    #print 'Reformatting '  + STUFF
    STUFF = re.sub(r', a song by', ' | ', STUFF)
    STUFF = re.sub(r' on Spotify', '', STUFF)
    STUFF = re.sub(r' - ', ' | ', STUFF).title()
    STUFF = re.sub(r'[\"\`]', '\'', STUFF)
    # I don't like brackets or ampersands, if you do, take this bit out
    STUFF = re.sub(r'[\(\[\{]', ' - ', STUFF)
    STUFF = re.sub(r'[\}\]\)]', ' ', STUFF)
    STUFF = re.sub(r'^ - ', '', STUFF)
    STUFF = re.sub(r'&', ' And ', STUFF)
    ###
    STUFF = re.sub(r'[\/]', '\ ', STUFF)
    STUFF = re.sub(r'   ', ' ', STUFF)
    STUFF = re.sub(r'  ', ' ', STUFF)
    STUFF = re.sub(r'\n', '', STUFF)
    #STUFF = re.sub(r' \| ', '|', STUFF)
    STUFF = re.sub(r'^[ ]$', '', STUFF)
    # Converting to unicode to avoid umluats breaking things
    # Also, title case all the things, CHVRCHES can stop being so damn fussy
    STUFF = unicode(STUFF).title()
    STUFF = re.sub(r'I\'M', 'I\'m', STUFF)
    STUFF = re.sub(r'\'S', '\'s', STUFF)
    STUFF = re.sub(r'\'S ', '\'s ', STUFF)
    STUFF = re.sub(r'\'T ', '\'t ', STUFF)
    STUFF = re.sub(r'\'D ', '\'d ', STUFF)
    STUFF = re.sub(r'\'Re ', '\'re ', STUFF)
    STUFF = re.sub(r'\'Ve ', '\'ve ', STUFF)
    STUFF = re.sub(r'\'Ll ', '\'ll ', STUFF)
    print STUFF
    return STUFF

def retryFunc(doThis,withThis):

    for attempt in range(1,20):
        try:
            goodStuff = doThis(withThis)
            break
        except (requests.exceptions.ConnectionError,URLError,HTTPError):
            time.sleep(2)
            print "try again"
            attempt += 1
            continue
    else:
        ohSmeg = "BadFunk " + doThis + withThis
        errorOut(ohSmeg)

        print doThis + withThis + " - Can't do shit\n"
        err = open('error.log','a+')
        err.write( doThis + withThis + " - Can't do shit\n") 
        goodStuff = None
    return goodStuff


def getTitleFromUrl(URLarg):
    #print "Getting title from " + URLarg
    soupTitle = BeautifulSoup(urllib2.urlopen(URLarg), "html.parser")
    URLarg = reformat(soupTitle.title.string)

    return URLarg


def processCSV(CSV):

    print 'Processing CSV!'
    f = open(CSV)
    line = f.readline()

    while line:
        if re.match(r'^(http|HTTP)', line):
            line = retryFunc(getTitleFromUrl,line)

        if line is not None:
            #processTrack(line)
            line = f.readline()
    f.close()
    sys.exit()



if __name__ == "__main__":
   checkOptions(sys.argv[1:])
