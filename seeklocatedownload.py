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

reload(sys)
sys.setdefaultencoding('utf8')

workDir = "files"
outputDir = "output"
mp3Tmp1 = workDir + "/tmp1.mp3"
mp3Tmp2 = workDir + "/tmp2.mp3"
jpgTmp = workDir + "/tmp.jpg"
REV = None


def makeTheDir(dirc):
    try: 
        os.makedirs(dirc)
    except OSError:
        if not os.path.isdir(dirc):
            os.makedirs(dirc)
            raise

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
        getUrl(TITLE,ARTIST)

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

def reformat(STUFF):
    print 'Reformatting '  + STUFF
    STUFF = re.sub(r', a song by', ' | ', STUFF)
    STUFF = re.sub(r' on Spotify', '', STUFF)
    STUFF = re.sub(r' - ', ' | ', STUFF).title()
    STUFF = re.sub(r' – ', ' | ', STUFF)
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
    STUFF = re.sub(r' \| ', '|', STUFF)
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
    STUFF = re.sub(r'\'Ll ', '\'ll ', STUFF)
    return STUFF



def getTitleFromUrl(URLarg):
    print "Getting title from " + URLarg
    soupTitle = BeautifulSoup(urllib2.urlopen(URLarg), "html.parser")
    URLarg = reformat(soupTitle.title.string)
    return URLarg


def retryFunc(funk,grr):
    for attempt in range(1,20):
        try:
            goodStuff = funk(grr)
            break
        except (requests.exceptions.ConnectionError,URLError,HTTPError):
            time.sleep(2)
            print "try again"
            attempt += 1
            continue
    else:
        ohSmeg = funk + grr
        errorOut(ohSmeg)

        print funk + grr + " - Can't do shit\n"
        err = open('error.log','a+')
        err.write( funk + " - Can't do shit\n") 
        goodStuff = None
    return goodStuff


def processCSV(CSV):

    print 'Processing CSV!'
    f = open(CSV)
    line = f.readline()

    while line:
        if re.match(r'^(http|HTTP)', line):
            line=retryFunc(getTitleFromUrl,line)
        if line is not None:
            processTrack(line)
            line = f.readline()
    f.close()
    sys.exit()


def processTrack(TRACK):
    global REV

    TRACK = reformat(TRACK)

    splitTrack = TRACK.split("|")

    if len(splitTrack) < 2:
        TITLE = TRACK
        ARTIST = None
    else:
        if REV is not None:
            print "CSV is Artist|Title"
            TITLE = splitTrack[-1]
            splitTrack.pop() 
            ARTIST = ' - '.join(splitTrack)
        else:
            print "CSV is Title|Artist"
            ARTIST = splitTrack[-1]
            splitTrack.pop() 
            TITLE = ' - '.join(splitTrack)
    getUrl(TITLE,ARTIST)

def getUrl(TITLE,ARTIST):

    if ARTIST is None:
        textToSearch = TITLE
        ARTIST = 'Unknown'
    if TITLE is None:
        textToSearch = ARTIST
        TITLE = 'Unknown'
    else:
        textToSearch = ARTIST + " " + TITLE

    mp3Out = outputDir + "/" + ARTIST + " - " + TITLE + ".mp3"

    if os.path.isfile(mp3Out):
        skipIt(mp3Out)
    else:
        print "getting URL for " + textToSearch

        # Removing special characters from search string
        rx = re.compile('\W+')
        textToSearch = rx.sub(' ', textToSearch).strip()

        query = urllib.quote(textToSearch)

        def youtubeUrlGetter(query):
            youtube = "https://www.youtube.com/results?search_query=" + query
            response = urllib2.urlopen(youtube)
            html = response.read()
            soup = BeautifulSoup(html, "html.parser")
            for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'})[:1]:
                RESULTURL = 'https://www.youtube.com' + vid['href']
                RESULTURL = RESULTURL.split('\n', 1)[0]
            return RESULTURL

        RESULTURL = retryFunc(youtubeUrlGetter,query)
        if RESULTURL is None or RESULTURL.find("/channel/") != -1:
            errorOut(RESULTURL)
        else:
            downloadFile(TITLE,ARTIST,RESULTURL)

    print "getting URL for " + textToSearch

    # Removing special characters from search string
    rx = re.compile('\W+')
    textToSearch = rx.sub(' ', textToSearch).strip()

    query = urllib.quote(textToSearch)

    def youtubeUrlGetter(query):
        youtube = "https://www.youtube.com/results?search_query=" + query
        response = urllib2.urlopen(youtube)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'})[:1]:
            RESULTURL = 'https://www.youtube.com' + vid['href']
        return RESULTURL

    RESULTURL = retryFunc(youtubeUrlGetter,query)
    if RESULTURL is not None:
        downloadFile(TITLE,ARTIST,RESULTURL)

def downloadFile(TITLE,ARTIST,RESULTURL):
    global workDir
    global outputDir
    global mp3Tmp1
    global jpgTmp
    DESCRIPTION = None

    mp3Out = outputDir + "/" + ARTIST + " - " + TITLE + ".mp3"
    if os.path.isfile(mp3Out):
        skipIt(mp3Out)
    else:

        makeTheDir(workDir)
        cleanFiles = os.listdir(workDir)
        for file in cleanFiles:
            os.remove(os.path.join(workDir,file))

        def downloader(URL):
            global workDir
            print "Downloading " + TITLE + ' by ' + ARTIST + ' from ' + RESULTURL
            ydl_opts = {
            'ignoreerrors': 'true',
            'noplaylist': 'true',
            'writethumbnail': (workDir +'/%(title)s-.jpg'),
            'format': 'bestaudio/best',
            'outtmpl': (workDir +'/%(title)s|%(artist)s|%(track)s|%(album)s|%(release_year)s|%(genre)s|%(track_number)s|%(album_artist)s|-BATMAN|.tmp'), 
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'progress_hooks': [my_hook],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([RESULTURL + ' -s'])

        DOWNLOAD = retryFunc(downloader,RESULTURL)
        

    makeTheDir(workDir)
    cleanFiles = os.listdir(workDir)
    for file in cleanFiles:
        os.remove(os.path.join(workDir,file))

    def downloader(URL):
        global workDir
        print "Downloading " + TITLE + ' by ' + ARTIST + ' from ' + RESULTURL
        print subprocess.Popen("youtube-dl \'" + URL + "\' --no-playlist -o \'" + workDir + "/%(title)s.mp3\' -x --embed-thumbnail", shell=True, stdout=subprocess.PIPE).stdout.read()
        return 'Downloaded'

    DOWNLOAD = retryFunc(downloader,RESULTURL)

    if DOWNLOAD is not None:
        newFiles = os.listdir(workDir)
        for file in newFiles:
            if file.endswith(".jpg"):
                os.rename(os.path.join(workDir,file), jpgTmp )
            else:
                DESCRIPTION = file    
                os.rename(os.path.join(workDir,file), mp3Tmp1 )
       
        if DESCRIPTION is None:
            errorOut('file is not there' + TITLE + ' ' + ARTIST + ' ' + RESULTURL)
        else:
            convertFile(TITLE,ARTIST,DESCRIPTION)

        ## Pretty sure this bit is redundant thanks to the writethumbnail ydl option
        if not os.path.isfile( jpgTmp ):
            thumbNailUrl = subprocess.Popen("youtube-dl \'" + RESULTURL + "\' --get-thumbnail ", shell=True, stdout=subprocess.PIPE).stdout.read()
            thumbNailUrl = thumbNailUrl.split('\n', 1)[0]
            thumbNail = urllib2.urlopen(thumbNailUrl)
            with open(jpgTmp,'wb') as output:
              output.write(thumbNail.read())

        WHOOPS = " Can't download " + TITLE + " - " + ARTIST + " from " + RESULTURL + " sorrynotsorry"



def convertFile(TITLE,ARTIST,DESCRIPTION):
    global mp3Tmp1
    global mp3Tmp2
    global jpgTmp
    global outputDir

    mp3Out = outputDir + "/" + ARTIST + " - " + TITLE + ".mp3"

    if os.path.isfile(mp3Out):
        skipIt(mp3Out)
    else:
        makeTheDir(outputDir)

        # Reformatting the description, we don't have to be as fussy here

        DESCRIPTION = re.sub(r'[\"]', " ", DESCRIPTION)
        DESCRIPTION = re.sub(r"\|NA\|", "||", DESCRIPTION)
        DESCRIPTION = re.sub(r"\|NA\|", "||", DESCRIPTION)
        splitTrack = DESCRIPTION.split("|")

        print "Description " + DESCRIPTION

        origTitle = splitTrack[0]
        if splitTrack[1] != '':
            ARTIST = splitTrack[1]
            ARTIST = reformat(ARTIST)
        if splitTrack[2] != '':
            TITLE = splitTrack[2]
            TITLE = reformat(TITLE)

        newAlbum = splitTrack[3]
        newRelYear = splitTrack[4]
        newGenre = splitTrack[5]
        newTrackNumber = splitTrack[6]
        newAlbumArtist = splitTrack[7]

        print "Adding metadata to " + TITLE + ' by ' + ARTIST

        if os.path.isfile( jpgTmp ):
            COVER = "Cover (front)"
            print "Adding Cover to " + TITLE + ' by ' + ARTIST
            addCover = " -i \"" + jpgTmp + "\"  -map 0 -map 1 -metadata:s:v title=\"" + COVER + "\""
        else:
            addCover = ''

        # Should probably replace this with the ffmpeg python module, but I couldn't be bothered right now
        print subprocess.Popen("ffmpeg -hide_banner -nostats -loglevel error -i \"" + mp3Tmp1 + "\"  " + addCover + "  \
            -metadata title=\"" + TITLE + "\" -metadata ARTIST=\"" + ARTIST + "\" \
            -metadata album=\"" + newAlbum + "\" -metadata year=\"" + newRelYear + "\"\
            -metadata genre=\"" + newGenre + "\" -metadata track=\"" + newTrackNumber + "\"\
            -metadata album_artist=\"" + newAlbumArtist + "\" -metadata comment=\"" + origTitle + "\"\
            -c copy -y \'" + mp3Tmp2 + "\' ", shell=True, stdout=subprocess.PIPE).stdout.read()
        # Can you tell I originally wrote this in bash?

        print "Renaming to " + mp3Out
        os.rename(mp3Tmp2, mp3Out )

        if not os.path.isfile(mp3Out):
            print "ruh roh!"
            oops = TITLE + ' - ' + ARTIST + ' - ' + DESCRIPTION + " - File not converted\n"
            errorOut(oops)

        print "Done!"
        print
        print "#############"
        print 

def errorOut(oops):
    print "Whoops"
    print "Can't do " + oops
    err = open('error.log','a+')
    err.write( oops + " - feck!\n") 

def skipIt(bopIt):
    print bopIt + " already exists, skipping"

if __name__ == "__main__":
   checkOptions(sys.argv[1:])
