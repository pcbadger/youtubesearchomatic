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
guessTags     = ''

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
    print "Asking Google to search as it's a bit more forgiving than discogs: " + q
    print "This is a bit more prone to inaccuracy though"
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
        print "Discogs URL " + str(result)
        result =  "https://www.discogs" + str(result).rsplit("+&amp;cd",1)[0]
        print "result ID " + str(result)
    except:
        result = "ATTRIBUTE_ERROR"
        print "Can't find a webcache URL"
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
	ans  = soup.find('a', attrs={'class' : 'spell'})
	if ans:
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
	else:
		result = ''
	if result and result != q and result != "ATTRIBUTE_ERROR":
		print "Google says did you mean .... " + str(result)
	else:
		result = ''
		print "No new match!"
	return result


def fixCase(stringToFixIn):
	print "FIXING case " + stringToFixIn
	stringToFix = unicode(stringToFixIn).title().strip()
	stringToFix = re.sub(r"’", "\'", stringToFix)
	stringToFix = re.sub(r"n(\ |\')(T|t) ", "n\'t ", stringToFix)
	stringToFix = re.sub(r"(\ |\')(S|s) ", "\'s ", stringToFix)
	stringToFix = re.sub(r"(\ |\')(V|v)e ", "\'ve ", stringToFix)
	stringToFix = re.sub(r"(\ |\')(L|l)l ", "\'ll ", stringToFix)
	stringToFix = re.sub(r"(\ |\')(R|r)e ", "\'re ", stringToFix)
	stringToFix = re.sub(r" I(\ |\')M ", " I\'m ", stringToFix)
	print "Fixed Case " + stringToFix
	return stringToFix

def sanitiseString(tagToCheck,superHarsh):
	# Strip all the crap out of the string, maybe we'll get a result now
	sanitisedTagToCheck = ''
	tagToCheck=tagToCheck.strip()
	rx = re.compile('\W+')
	print "Sanitising this tag: " + tagToCheck
	tagIn = rx.sub(' ', tagToCheck).strip()
	tagIn = str(str.lower(str(tagIn))).strip()
	print "Debug Sanitise pass 1 " + tagIn
	tagIn = re.sub(r'mp3$', '', tagIn)
	print "Debug Sanitise pass 2 " + tagIn

	tagIn = re.sub(r'ogg$', '', tagIn)
	tagIn = re.sub(r'( by | hd|HQ|720p|1080p|official|remaster|mono|stereo)', ' ', tagIn, re.IGNORECASE)
	tagIn = re.sub(r'(audio|video)$', ' ', tagIn, re.IGNORECASE)
	tagIn = re.sub(r'  ', ' ', tagIn)
	if tagIn == str(tagToCheck) and superHarsh == 0:
		print "Debug Sanitise pass 3 " + tagIn
		print "Sanitising had no effect!"
		tagIn = ''
	else:
		print "SANITISED: " + str(tagIn)
	return tagIn

def extractAlbumTitle(albumTitleToCheck,artistToCheck):
	albumTitle  = str.lower(str(albumTitleToCheck))
	artist      = str.lower(str(artistToCheck))
	tmpArtist   = re.sub(r'\&', 'And', artist)
	#Discogs will often prefix the name of a release with the artists name and we want to strip that out
	albumTitle  = re.sub(r'\* - ', ' - ', albumTitle)
	albumTitle  = re.sub(r'^' + re.escape(artist) + ' - ', '', albumTitle)
	albumTitle  = re.sub(r'^' + re.escape(tmpArtist) + ' - ', '', albumTitle)
	return albumTitle

def stripThe(artistName):
	theLessArtist = re.sub(r"^(T|t)he ", '', str.lower(str(artistName))).split(", ",1)[0]
	theLessArtist = sanitiseString(re.sub(r" & ", ' and ', theLessArtist).split(" (",1)[0],1)
	return theLessArtist

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


	print "Filename: " + str(fileName) + ' ' + str(mp3info)

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
		titleFromFile = sanitiseString(mp3FileName,1)

		checkTitleOnGoogle = gSuggDidYouMean(str(titleFromFile))
		if checkTitleOnGoogle and checkTitleOnGoogle != "ATTRIBUTE_ERROR":
			titleFromFile = checkTitleOnGoogle
		sQ1 = str(titleFromFile)

	if 'TAG_IS_EMPTY' in (ipArtist,ipTitle,ipAlbumTitle,ipReleaseYear,ipGenre,ipCover):

		print 'Go Get Info: ' + str(sQ1) + " " + str(sQ2)
		if searchDiscogs(sQ1,sQ2):
			# if positive results are returned, exit out and return a result, this will enable addTagsToFile to start
			return "Cool!"

	else:
		print "File OK: " + ipArtist + " " + ipTitle,
		moveTheFile(mp3FileName,'OUTPUT_2_ALREADY_GOOD')
		return ''

def searchDiscogs (sQ1,sQ2):
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

	print "sQ1 " + str(sQ1)
	print "sQ2 " + str(sQ2)
	searchQuery   = sQ1.strip() + ' ' + sQ2.strip()

	idFromGoogle  = ""
	opArtist      = 'TAG_IS_EMPTY'
	opTitle       = 'TAG_IS_EMPTY'
	opAlbumTitle  = 'TAG_IS_EMPTY'
	opAlbumArtist = 'TAG_IS_EMPTY'
	opReleaseYear = 'TAG_IS_EMPTY'
	opGenre       = 'TAG_IS_EMPTY'
	opCover       = 'TAG_IS_EMPTY'
	useThisAlbum  = '0'
	count         = 0

	discogs = discogs_client.Client('ExampleApplication/0.1', user_token="tLOqGxpsHNYovSMEvRsFXgtAfXKOfIBRwbhkiepw")

	results = discogs.search(searchQuery, type='release')
	print "results " + str(results)
	time.sleep(2)
	results.pages
	1
	try:
		opAlbumTitle  = extractAlbumTitle(results[0].title,results[0].artists[0].name)
		while useThisAlbum == "0":
			# The first result tends to be a single release and we'd rather have an actual album, so iterating through the results
			time.sleep(1)
			thisTitle = str.lower(str(results[count].title))
			thisName = str.lower(str(results[count].artists[0].name))
			currentAlbumTitle = extractAlbumTitle(thisTitle,thisName)
			checkTitle = sanitiseString(str.lower(str(sQ2)),1)

			if str.lower(str(currentAlbumTitle)) != checkTitle and stripThe(ipArtist) == stripThe(thisName):
				print "Release title doesn't match track title and the artist name matches, this is probably an album"
				releaseNumber = count
				resultId      = str(results[releaseNumber].id)
				masterRelease = discogs.release(resultId)
				allTracks     = masterRelease.tracklist

				for key in allTracks:
					keyTrackTitle = str.lower(str(key.title))
					keyTrackTitle = sanitiseString(keyTrackTitle,1)
					print "Debug Key Track title " + str(keyTrackTitle)
					print "Debug Track title " + str(checkTitle)
					if keyTrackTitle == checkTitle:
						print "Found an exact match for this track title in this album, using this release"
						useThisAlbum = "1"
						releaseNumber = count
						break
					else:
						splitTitle = sQ2.split(" - ",1)[0]
						print "Split Title " + str(splitTitle)
						if splitTitle == sQ2:
							print "Title or artist doesn't match, checking next title"
						else:
							print "SEARCHING DISCOGS WITH CHOPPED STRING!"
							searchDiscogs(sQ1,splitTitle)
							return ''
				print "Didn't find an exact match for this track title in this album, checking the next album"
				count = count + 1
				if count > 30:
					print "Couldn't find an album that exactly matched the track title, using first release 1"
					useThisAlbum = "1"
					releaseNumber = 0
					print
			else:
				print "Release title matches track title, this is probably a single. Either that or the artist name doesn't match. Checking the next release"
				count = count + 1
				if count > 30:
					print "Couldn't find an album that exactly matched the track title, using first release 2"
					useThisAlbum = "1"
					releaseNumber = 0
					print

		firstRelease = results[releaseNumber]
        
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
			print "Response: " + str(response)
			# None of this google stuff works right now, just bypass it.
			moveTheFile(mp3FileName,'OUTPUT_7_GOOGLE')
			return ''
		else:
			print "NO RESULTS! SANITISING"
			searchQuery = sQ1 + ' ' + sQ2.split(" - ",1)[0]
			sanitised = sanitiseString(searchQuery,0)
			if sanitised:
				print "SEARCHING DISCOGS WITH CLEAN STRING!"
				searchDiscogs(sanitised,"")
				return ''
			googleIt = googSearchDiscog(str(searchQuery))
			print "Google response: " + str(googleIt)
			idFromGoogle = googleIt.rsplit('/', 1)[-1]
			print "ID from Google: " + str(idFromGoogle)

	if firstRelease:
		print "Using release " + str(firstRelease)
		resultId = str(results[releaseNumber].id)
		print 'Result ID: ' + resultId

	elif idFromGoogle and idFromGoogle != "ATTRIBUTE_ERROR":
		print "Got an ID from google: it's " +  idFromGoogle
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

	try:

		if firstRelease:
			masterRelease = discogs.release(resultId)
		
		elif idFromGoogle and idFromGoogle != "ATTRIBUTE_ERROR":
			masterRelease = discogs.release(idFromGoogle)
			
		print "Debug master: " + str(masterRelease)

		try:		
			opAlbumTitle  = masterRelease.title
		except:
			opAlbumTitle  = "TAG_IS_EMPTY"
		try:		
			artistInfo    = masterRelease.artists[0]
			opArtist      = artistInfo.name
		except:
			opArtist      = "TAG_IS_EMPTY"
		try:		
			opReleaseYear = masterRelease.year
		except:
			opReleaseYear = "TAG_IS_EMPTY"
		try:		
			opGenre       = masterRelease.genres[0]
		except:
			opGenre       = "TAG_IS_EMPTY"
		try:		
			opCover       = masterRelease.images[0]['uri']
		except:
			opCover  = "TAG_IS_EMPTY"

		if opArtist != "TAG_IS_EMPTY":
			opAlbumTitle  = extractAlbumTitle(opAlbumTitle,opArtist)
		
		opAlbumTitle  = fixCase(opAlbumTitle)
		print "USING RELEASE " + str(opAlbumTitle)

	except :
		print "NO RELEASE or MISSING SOME FIELDS 1"
		moveTheFile(mp3FileName,'OUTPUT_8_NOT_SURE_WHATS_WRONG')
		return ''

	opArtist       = re.sub(r' \(([0-9])\)', '', artistInfo.name)

	if re.search(r'various|varios',opArtist, re.IGNORECASE):
		opAlbumArtist = "Various"

	if "TAG_IS_EMPTY" in (opArtist,opAlbumTitle,opAlbumArtist,opReleaseYear,opGenre,opCover):
		print "SOME RESULTS, BUT NOT GOOD ENOUGH 1"
		goCheckGoogle = gSuggDidYouMean(str(searchQuery))
		if goCheckGoogle and goCheckGoogle != "ATTRIBUTE_ERROR":
			"Got something from Google, Going for another pass 2: "
			searchDiscogs (goCheckGoogle,"")
		elif goCheckGoogle and goCheckGoogle == "ATTRIBUTE_ERROR":
			moveTheFile(mp3FileName,'OUTPUT_4_NO_RESULTS')
		else:
			print "ALBUM: "  + opAlbumTitle
			print "ARTIST: " + opArtist
			print "ALBUM ARTIST: " + opAlbumArtist
			print "YEAR: "   + str(opReleaseYear)
			print "GENRE: "  + opGenre
			print "COVER: "  + opCover
			guessTags = 1
			insertNewTags(filepath)
		return 'true'

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

	global guessTags

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

	if ipGenre  		== "TAG_IS_EMPTY":
		if opGenre == "TAG_IS_EMPTY":
			opGenre = "Music"
		print 'Adding ' + opGenre + ' to ID3 ipGenre ;',
		newTag.add(TCON(encoding=3, text=opGenre))

	if ipArtist  		== "TAG_IS_EMPTY":
		print 'Adding ' + opArtist + ' to ID3 ipArtist ;',
		opArtist = fixCase(opArtist)
		newTag.add(TPE1(encoding=3, text=opArtist))

	if ipReleaseYear  	== "TAG_IS_EMPTY":
		if opReleaseYear == "TAG_IS_EMPTY":
			opReleaseYear = 0000
		print 'Adding ' + str(opReleaseYear) + ' to ID3 ipReleaseYear ;',
		newTag.add(TDRC(encoding=3, text=str(opReleaseYear)))

	if ipCover    == "TAG_IS_EMPTY":
		if opCover == "TAG_IS_EMPTY":
			jpgTmp = "wat.jpg"
		try:
			coverFile = urllib2.urlopen(opCover)
			with open(jpgTmp,'wb') as output:
				output.write(coverFile.read())
		except:
			print "Whoops! Something, something, cover url, something"
		pic = APIC(3, u'image/jpg', 3, u'Front cover', open(jpgTmp, 'rb').read())
		newTag.add(pic)
		print 'Adding Cover ;',

	if ipTitle    == "TAG_IS_EMPTY" or titleFromFile or ipAlbumTitle == "TAG_IS_EMPTY":
		opTitle = sanitiseString(mp3FileName,1)
		opTitle = str.lower(str(opTitle))
		tmpArtist = str.lower(str(opArtist))
		opTitle = re.sub(r'^' + re.escape(tmpArtist) , '', opTitle)
		opTitle = re.sub(r'^' + re.escape(str.lower(str(ipArtist))) , '', opTitle)
		opTitle = re.sub(r'  ', ' ', opTitle)
		opTitle = sanitiseString(opTitle,1)
		opTitle = fixCase(opTitle)
		if ipAlbumTitle == "TAG_IS_EMPTY" and opAlbumTitle == "TAG_IS_EMPTY":
			opAlbumTitle = opTitle
		elif ipTitle    == "TAG_IS_EMPTY" or titleFromFile:
			print "Adding ID3 ipTitle ;" + ipTitle + ' ' + titleFromFile
			newTag.add(TIT2(encoding=3, text=opTitle))

	if ipAlbumArtist  	== "TAG_IS_EMPTY":
		if opAlbumArtist == "TAG_IS_EMPTY":
			opAlbumArtist = ipArtist
		opAlbumArtist = fixCase(opAlbumArtist)
		print 'Adding ' + opAlbumArtist + ' to ID3 ipAlbumArtist ;',
		newTag.add(TPE2(encoding=3, text=opAlbumArtist))

	if ipAlbumTitle  	== "TAG_IS_EMPTY":
		print 'Adding ' + opAlbumTitle + ' to ID3 ipAlbumTitle ;',
		opAlbumTitle = fixCase(opAlbumTitle)
		newTag.add(TALB(encoding=3, text=opAlbumTitle))

	newTag.save()

	if "TAG_IS_EMPTY" in (opArtist,opAlbumTitle,opAlbumArtist,opReleaseYear,opGenre,opCover) or guessTags == 1:
		print "SOME RESULTS, BUT NOT GOOD ENOUGH 2!"
		moveTheFile(mp3FileName,'OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH')
	elif stripThe(opAlbumArtist) != stripThe(ipArtist) and opAlbumArtist != "Various":
		moveTheFile(mp3FileName,'odd')
	else:
		moveTheFile(mp3FileName,'OUTPUT_1_PROCESSED')

for subdir, dirs, files in os.walk(inputFileDir):
	for file in files:

		filepath = subdir + os.sep + file
		mp3FileName = file
		if re.search(r'mp3$', filepath, re.IGNORECASE):
			getTagsFromFile(filepath)
