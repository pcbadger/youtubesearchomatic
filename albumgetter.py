#!/usr/bin/python
# -*- coding: utf-8 -*-
import discogs_client
import os
import re
import urllib2
import time
import requests
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC, APIC


import io
import gzip
import sys
import urllib

from bs4 import BeautifulSoup
from StringIO import StringIO

from mutagen import File
import sys

reload(sys)
sys.setdefaultencoding('utf8')

inputFileDir  = 'inputfiles'
mp3FileName   = ''
titleFromFile = ''

def moveTheFile(sourceFileName,destinationFolder):
	global mp3FileName
	print '\n'
	print "Moving " + sourceFileName + " to " + destinationFolder
	destinationFile = destinationFolder + '/' + mp3FileName
	sourceFile = inputFileDir + '/' + sourceFileName
	try: 
		os.makedirs(destinationFolder)
	except OSError:
		if not os.path.isdir(destinationFolder):
			os.makedirs(destinationFolder)
			raise
	os.rename(sourceFile, destinationFile )
	print '#################################'
	print '\n'
	return ''


def checkForJunkEntry(tagToCheck):
	if re.match(r'^(unknown|na|n\/A|none|null|varios|various|various artists|varios artists|\ )$', tagToCheck, re.IGNORECASE):
		print "JUNK TAG: " + tagToCheck
		tagToCheck = 'TAG_IS_EMPTY'
	return tagToCheck


def gSuggGetPage(url):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    request.add_header('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()
    return data


def googSearchDiscog(q):
    print  "Asking Google to search as it's a bit more forgiving than discogs: " + q
    q = str(str.lower(q)).strip() + " site:discogs.com"
    url = "http://www.google.com/search?q=" + urllib.quote(q)
    print "Searching google with URL "  + str(url)
    html = gSuggGetPage(url)
    soup = BeautifulSoup(html, "html.parser")
    ans = soup.find('a', attrs={'class' : 'spell'})
    try:
    	# Looking for webcache URL, rather than the one in <cite> because sometimes that's truncated
        result = soup.select_one("a[href*=webcache*release]")
        print "Raw URL " + str(result)
        result =  str(result).split("https://www.discogs",1)[1]
        print "Discogs ULR " + str(result)
        result =  "https://www.discogs" + str(result).rsplit("+&amp;cd",1)[0]
        print "result ID " + str(result)
    except:
        result = "ATTRIBUTE_ERROR"
    print "Google search of Discogs result: " + str(result)
    if result == q:
    	result = ''
    	print "No new match!"
    return result


def gSuggDidYouMean(q):
    print  "Asking Google about: " + q
    q = str(str.lower(q)).strip()
    url = "http://www.google.com/search?q=" + urllib.quote(q)
    print "Searching google with URL " + str(url)
    html = gSuggGetPage(url)
    soup = BeautifulSoup(html, "html.parser")
    ans = soup.find('a', attrs={'class' : 'spell'})
    try:
        result = repr(ans.contents)
        result = result.replace("u'","")
        result = result.replace("/","")
        result = result.replace("<b>","")
        result = result.replace("<i>","")
        result = re.sub('[^A-Za-z0-9\s]+', '', result)
        result = re.sub(' +',' ',result)
    except AttributeError:
        result = "ATTRIBUTE_ERROR"
    print "Google says did you mean .... " + str(result)
    if result == q:
    	result = ''
    	print "No new match!"
    return result


def fixCase(stringToFixIn):
	print "FIXING " + stringToFixIn
	stringToFix = unicode(stringToFixIn).title().strip()
	print "fixed " + stringToFix
	stringToFix = re.sub(r'n T ', "n\'t ", stringToFix)
	stringToFix = re.sub(r' S ', "\'s ", stringToFix)
	stringToFix = re.sub(r' Ve ', "\'Ve ", stringToFix)
	stringToFix = re.sub(r' Ll ', "\'ll ", stringToFix)
	return stringToFix

def sanitiseString(tagToCheck):
	# Strip all the crap out of the string, maybe we'll get a result now
	sanitisedTagToCheck = ''
	rx = re.compile('\W+')
	print "Sanitising this tag: " + tagToCheck
	tagIn = rx.sub(' ', tagToCheck).strip()
	tagIn = str(str.lower(str(tagIn))).strip()
	print "1 " + tagIn
	tagIn = re.sub(r'mp3$', '', tagIn)
	print "2 " + tagIn

	tagIn = re.sub(r'ogg$', '', tagIn)
	tagIn = re.sub(r'( by | hd|HQ|720p|1080p|official|remaster)', ' ', tagIn, re.IGNORECASE)
	tagIn = re.sub(r'(audio|video)$', ' ', tagIn, re.IGNORECASE)
	tagIn = re.sub(r'  ', ' ', tagIn)
	if tagIn == str(tagToCheck):
		print "3 " + tagIn
		print "Sanitising had no effect!"
		tagIn = ''
	else:
		print "SANITISED: " + str(tagIn)
	return tagIn

def getTagsFromFile (fileName):
	global ipArtist
	global ipTitle
	global ipAlbumTitle
	global ipAlbumArtist
	global ipReleaseYear
	global ipGenre
	global ipCover
	global mp3FileName
	global titleFromFile

	titleFromFile = ''
	ipArtist      = 'TAG_IS_EMPTY'
	ipTitle       = 'TAG_IS_EMPTY'
	ipAlbumTitle  = 'TAG_IS_EMPTY'
	ipAlbumArtist = 'TAG_IS_EMPTY'
	ipReleaseYear = 'TAG_IS_EMPTY'
	ipGenre       = 'TAG_IS_EMPTY'
	ipCover       = 'TAG_IS_EMPTY'

	try:
		mp3info = EasyID3(fileName)
	except:
		#No ID3 Headers, adding them
		mp3info = mutagen.File(fileName, easy=True)
		mp3info.add_tags()
		mp3info
		mp3info.save()


	print fileName + ' ' + str(mp3info)

	def checkTag(varName,tagName):
		try:
			varName = mp3info[tagName][0]
			varName = checkForJunkEntry(varName)
		except KeyError:
			varName = 'TAG_IS_EMPTY'
		return varName

	ipAlbumTitle  = checkTag('ipAlbumTitle','album')
	ipAlbumArtist = checkTag('ipAlbumArtist','albumartist')
	ipGenre       = checkTag('ipGenre','genre')
	ipArtist      = checkTag('ipArtist','artist')
	ipTitle       = checkTag('ipTitle','title')

	if checkTag('ipReleaseYear','date'):
		ipReleaseYear = checkTag('ipReleaseYear','date')
		try:
			if int(ipReleaseYear) < 1900 or int(ipReleaseYear) > 2020 :
				ipReleaseYear = 'TAG_IS_EMPTY'
		except ValueError:
			ipReleaseYear = 'TAG_IS_EMPTY'

	try:
		artwork = File(fileName).tags['APIC:'].data
		ipCover = 'Cool!'
	except:
		pass

	sQ1 = ipArtist
	sQ2 = ipTitle
	
	if sQ1 == 'TAG_IS_EMPTY':
		sQ1 = ''

	if sQ2 == 'TAG_IS_EMPTY':
		sQ2 = ''

	searchQuery = sQ1 + ' ' + sQ2

	if searchQuery == ' ':
		print "No Artist or Title Tags! Taking a guess at them based on filename"
		titleFromFile = sanitiseString(mp3FileName)

		checkTitleOnGoogle = gSuggDidYouMean(str(titleFromFile))
		if checkTitleOnGoogle and checkTitleOnGoogle != "ATTRIBUTE_ERROR":
			titleFromFile = checkTitleOnGoogle
		searchQuery = str(titleFromFile)

	if 'TAG_IS_EMPTY' in (ipArtist,ipTitle,ipAlbumTitle,ipReleaseYear,ipGenre,ipCover):

		print 'Go Get Info: ' + searchQuery
		if searchDiscogs(searchQuery):
			# if positive results are returned, exit out and return a result, this will enable addTagsToFile to start
			return "Cool!"

	else:
		print 'File OK: ' + ipArtist + " " + ipTitle,
		moveTheFile(mp3FileName,'OUTPUT_2_ALREADY_GOOD')
		return ''

def searchDiscogs (searchQuery):
	global opArtist
	global opTitle
	global opAlbumTitle
	global opAlbumArtist
	global opReleaseYear
	global opGenre
	global opCover
	global mp3FileName
	global ipArtist
	global ipTitle
	global titleFromFile

	idFromGoogle  = ""
	opArtist      = 'TAG_IS_EMPTY'
	opTitle       = 'TAG_IS_EMPTY'
	opAlbumTitle  = 'TAG_IS_EMPTY'
	opAlbumArtist = 'TAG_IS_EMPTY'
	opReleaseYear = 'TAG_IS_EMPTY'
	opGenre       = 'TAG_IS_EMPTY'
	opCover       = 'TAG_IS_EMPTY'

	discogs = discogs_client.Client('ExampleApplication/0.1', user_token="tLOqGxpsHNYovSMEvRsFXgtAfXKOfIBRwbhkiepw")

	results = discogs.search(searchQuery, type='release')
	time.sleep(2)
	results.pages
	1
	try:
		firstRelease = results[0]

	except IndexError:
		print "NO RESULTS"
		firstRelease = ''
		response     = ''
		response     = gSuggDidYouMean(str(searchQuery))

		if response and response != searchQuery and response != "ATTRIBUTE_ERROR":
			ipTitle       = 'TAG_IS_EMPTY'
			ipArtist      = 'TAG_IS_EMPTY'
			titleFromFile = response
			print "Got response from Google, going for another pass"
			print response
			# None of this google stuff works right now, just bypass it.
			moveTheFile(mp3FileName,'OUTPUT_7_GOOGLE')
			return ''
		else:
			print "NO RESULTS! SANITISING"
			searchQuery = searchQuery.split(" - ",1)[0]
			sanitised = sanitiseString(searchQuery)
			if sanitised:
				print "SEARCHING DISCOGS WITH CLEAN STRING!"
				searchDiscogs(sanitised)
				return ''
			googleIt = googSearchDiscog(str(searchQuery))
			print googleIt
			idFromGoogle = googleIt.rsplit('/', 1)[-1]
			print idFromGoogle

	if firstRelease:
		print "first release " + str(firstRelease)
		resultId = str(results[0].id)

		try:
			print 'Result ID: ' + resultId
			masterRelease = discogs.master(resultId)

			try:				
				print "USING RELEASE"
				opAlbumTitle  = firstRelease.title
				artistInfo    = firstRelease.artists[0]
				opArtist      = artistInfo.name
				opReleaseYear = firstRelease.year
				opGenre       = firstRelease.genres[0]
				opCover       = firstRelease.images[0]['uri']

				tmpArtist     = re.sub(r'\&', 'And', opArtist)
				#Discogs will often prefix the name of a release with the artists name and we want to strip that out
				opAlbumTitle  = re.sub(r'\* - ', ' - ', opAlbumTitle)
				opAlbumTitle  = re.sub(r'^' + re.escape(opArtist) + ' - ', '', opAlbumTitle)
				opAlbumTitle  = re.sub(r'^' + re.escape(tmpArtist) + ' - ', '', opAlbumTitle)

			except :
				print "NO RELEASE or MISSING SOME FIELDS 1"
				try: 
					print "USING MASTER 1"
					# This code does nothing, no idea where I got it from.
					discogsSearchOutput = getDiscogsResultsFromMaster(masterRelease)
					# This has never happened so far
					moveTheFile(mp3FileName,'OUTPUT_7_MASTER_BUT_NO_RELEASE')
					return ''
				except:
					print "NO MASTER or MISSING SOME FIELDS"
					moveTheFile(mp3FileName,'OUTPUT_8_NO_RELEASE_NO_MASTER')
					return ''
				return ''

			opArtist       = re.sub(r' \(([0-9])\)', '', artistInfo.name)
			opAlbumArtist  = opArtist

			if re.search(r'various|varios',opArtist, re.IGNORECASE):
				opAlbumArtist = "Various"

		except:
			print "WHOOPS, can't get results[0].id"
			#moveTheFile(mp3FileName,'OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH')

			return ''
	elif idFromGoogle and idFromGoogle != "ATTRIBUTE_ERROR":
		print "Got an ID from google: it's " +  idFromGoogle
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

		try:
			print 'Result ID: ' + idFromGoogle
			masterRelease = discogs.release(idFromGoogle)
			print "master " + str(masterRelease)
			try:				
				print "USING RELEASE"
				opAlbumTitle  = masterRelease.title
				print str(masterRelease.title)
				artistInfo    = masterRelease.artists[0]
				opArtist      = artistInfo.name
				opReleaseYear = masterRelease.year
				opGenre       = masterRelease.genres[0]
				opCover       = masterRelease.images[0]['uri']
				tmpArtist     = re.sub(r'\&', 'And', opArtist)
				#Discogs will often prefix the name of a release with the artists name and we want to strip that out
				opAlbumTitle  = re.sub(r'\* - ', ' - ', opAlbumTitle)
				opAlbumTitle  = re.sub(r'^' + re.escape(opArtist) + ' - ', '', opAlbumTitle)
				opAlbumTitle  = re.sub(r'^' + re.escape(tmpArtist) + ' - ', '', opAlbumTitle)

			except :
				print "Something else went wrong. Can't use release"
				moveTheFile(mp3FileName,'OUTPUT_5_NOT_SURE_WHATS_WRONG')
				return ''

			opArtist       = re.sub(r' \(([0-9])\)', '', artistInfo.name)
			opAlbumArtist  = opArtist

			if re.search(r'various|varios',opArtist, re.IGNORECASE):
				opAlbumArtist = "Various"

		except:
			print "omething else went wrong. ID mismatch"
			moveTheFile(mp3FileName,'OUTPUT_5_NOT_SURE_WHATS_WRONG')
			return ''

	if "TAG_IS_EMPTY" in (opArtist,opAlbumTitle,opAlbumArtist,opReleaseYear,opGenre,opCover):
		print "SOME RESULTS, BUT NOT GOOD ENOUGH 1"
		goCheckGoogle = gSuggDidYouMean(str(searchQuery))
		if goCheckGoogle and goCheckGoogle != "ATTRIBUTE_ERROR":
			"Got something from Google, Going for another pass 2: "
			searchDiscogs (goCheckGoogle)
		else:
#			print "491"
			moveTheFile(mp3FileName,'OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH')
		return ''
	else:
		print "ALBUM: "  + opAlbumTitle
		print "ARTIST: " + opArtist
		print "ALBUM ARTIST: " + opAlbumArtist
		print "YEAR: "   + str(opReleaseYear)
		print "GENRE: "  + opGenre
		print "COVER: "  + opCover
		insertNewTags(filepath)
		return 'true'
	print "################################################### "


def insertNewTags(useThisFile):
	global opArtist
	global opTitle
	global opAlbumTitle
	global opAlbumArtist
	global opReleaseYear
	global opGenre
	global opCover
	global titleFromFile

	global ipArtist
	global ipTitle
	global ipAlbumTitle
	global ipAlbumArtist
	global ipReleaseYear
	global ipGenre
	global ipCover
	jpgTmp = 'tmp.jpg'

	newTag = ID3(useThisFile)


	def compareTags(tagToCheck,tagToWrite,ID3TagName):

		tagInContent = str(globals()[tagToCheck])

		print 'xxxxxx'
		print ID3TagName
		print tagToWrite
		print tagToCheck
		GOAT = globals()[ID3TagName]
		print "globals()[ID3TagName] " + str(GOAT)
		if tagInContent  == "TAG_IS_EMPTY":
			print 'Adding ' + str(tagInContent) + ' to ID3 ' + str(tagToCheck) + ' ;',
			newTag.add(GOAT(encoding=3, text=tagToWrite))

	if ipAlbumTitle  	== "TAG_IS_EMPTY":
		print 'Adding ' + opAlbumTitle + ' to ID3 ipAlbumTitle ;',
		newTag.add(TALB(encoding=3, text=opAlbumTitle))

	if ipAlbumArtist  	== "TAG_IS_EMPTY":
		print 'Adding ' + opAlbumArtist + ' to ID3 ipAlbumArtist ;',
		newTag.add(TPE2(encoding=3, text=opAlbumArtist))

	if ipGenre  		== "TAG_IS_EMPTY":
		print 'Adding ' + opGenre + ' to ID3 ipGenre ;',
		newTag.add(TCON(encoding=3, text=opGenre))

	if ipArtist  		== "TAG_IS_EMPTY":
		print 'Adding ' + opArtist + ' to ID3 ipArtist ;',
		newTag.add(TPE1(encoding=3, text=opArtist))

	if ipReleaseYear  	== "TAG_IS_EMPTY":
		print 'Adding ' + str(opReleaseYear) + ' to ID3 ipReleaseYear ;',
		newTag.add(TDRC(encoding=3, text=str(opReleaseYear)))


	if ipCover    == "TAG_IS_EMPTY":
		coverFile = urllib2.urlopen(opCover)
		with open(jpgTmp,'wb') as output:
			output.write(coverFile.read())
		pic = APIC(3, u'image/jpg', 3, u'Front cover', open(jpgTmp, 'rb').read())
		newTag.add(pic)
		print 'Adding Cover ;',

	if ipTitle    == "TAG_IS_EMPTY" or titleFromFile:
		print "Adding ID3 ipTitle ;" + ipTitle + ' ' + titleFromFile
		opTitle = sanitiseString(mp3FileName)
		opTitle = str.lower(str(opTitle))
		tmpArtist = str.lower(str(opArtist))
		opTitle = re.sub(r'^' + re.escape(tmpArtist) , '', opTitle)
		opTitle = re.sub(r'  ', ' ', opTitle)
		opTitle = sanitiseString(opTitle)
		opTitle = fixCase(opTitle)
		newTag.add(TIT2(encoding=3, text=opTitle))

	newTag.save()
	moveTheFile(mp3FileName,'OUTPUT_1_PROCESSED')

for subdir, dirs, files in os.walk(inputFileDir):
	for file in files:

		filepath = subdir + os.sep + file
		mp3FileName = file
		if re.search(r'mp3$', filepath, re.IGNORECASE):
			getTagsFromFile(filepath)
