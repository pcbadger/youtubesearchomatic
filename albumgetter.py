#!/usr/bin/python
# -*- coding: utf-8 -*-
import discogs_client
#import eyed3
import os
import re
import urllib2

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


#from mutagen.flac import File, Picture, FLAC
from mutagen import File
import sys


def makeTheDir(dirc):
    try: 
        os.makedirs(dirc)
    except OSError:
        if not os.path.isdir(dirc):
            os.makedirs(dirc)
            raise

reload(sys)
sys.setdefaultencoding('utf8')

mp3FileName = ''
titleFromFile = ''

def checkForJunkEntry(tagToCheck):

	#print "Checking " +  tagToCheck
	#if re.match(r'^(http|HTTP)', line)
	#tagToCheck = tagToCheck.sub(r'  ', ' ', tagToCheck)
	if re.match(r'^(unknown|na|n\/A|none|null|\ )$', tagToCheck, re.IGNORECASE):
		#print "BAD " + tagToCheck
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

def gSuggDidYouMean(q):
    print q
    q = str(str.lower(q)).strip()
    url = "http://www.google.com/search?q=" + urllib.quote(q)
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
        result = 1
    print result
    if result == q:
    	result = ''
    	print "no new match!"
    return result


def sanitiseString(tagToCheck):
	# Strip all the crap out of the string, maybe we'll get a result now
	# Bit of a last ditch effort this
	sanitisedTagToCheck = ''
	rx = re.compile('\W+')
	#print "this tag0 " + tagToCheck
	tagIn = rx.sub(' ', tagToCheck).strip()
	#print "this tag1 " + tagIn
	tagIn = re.sub(r'(live|audio|hd|HQ|1080p|official|video)', ' ', tagIn, re.IGNORECASE)
	#print "this tag2 " + tagIn
	tagIn = re.sub(r' (\([0-9])\w+\)', '', tagIn)
	#print "this tag3 " + tagIn
	tagIn = re.sub(r'  ', ' ', tagIn)
	checkGoogle = gSuggDidYouMean(str(tagIn))
	#print "this tag4 " + tagIn
	if checkGoogle:
		if checkGoogle != str(tagToCheck):
			sanitisedTagToCheck = checkGoogle	
	else:
		if tagIn != str(tagToCheck):
			sanitisedTagToCheck = tagIn	
		
	print "SANITISED: " + str(sanitisedTagToCheck)
	return sanitisedTagToCheck

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

	ipArtist      = 'TAG_IS_EMPTY'
	ipTitle       = 'TAG_IS_EMPTY'
	ipAlbumTitle  = 'TAG_IS_EMPTY'
	ipAlbumArtist = 'TAG_IS_EMPTY'
	ipReleaseYear = 'TAG_IS_EMPTY'
	ipGenre       = 'TAG_IS_EMPTY'
	ipCover       = 'TAG_IS_EMPTY'

	source        = 'inputfiles/' + mp3FileName
	try:
		mp3info = EasyID3(fileName)
	except:
		#try:
		#	mp3info = EasyID3(fileName)
		#except mutagen.id3.ID3NoHeaderError:
		mp3info = mutagen.File(fileName, easy=True)
		mp3info.add_tags()
		mp3info
		mp3info.save()
		#destination="OUTPUT_5_WEIRD/" + mp3FileName
		#makeTheDir("OUTPUT_5_WEIRD")
		#os.rename(source, destination )
		#return ''

	print fileName + str(mp3info)

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

	if ipArtist == 'TAG_IS_EMPTY':
		sQ1 = ''
	else:
		sQ1 = ipArtist

	if ipTitle == 'TAG_IS_EMPTY':
		sQ2 = ''
	else:
		sQ2 = ipTitle

	if checkTag('ipReleaseYear','date'):
		ipReleaseYear = checkTag('ipReleaseYear','date')
		try:
			if int(ipReleaseYear) < 1900 or int(ipReleaseYear) > 2020 :
				ipReleaseYear = 'TAG_IS_EMPTY'
		except ValueError:
			ipReleaseYear = 'TAG_IS_EMPTY'

	try:
		#file    = File(fileName) 
		artwork = File(fileName).tags['APIC:'].data
		ipCover = 'Cool!'
	except:
		pass

	searchQuery = sQ1 + ' ' + sQ2

	if searchQuery == ' ':
		#Get some tags then

		titleFromFile = re.sub(r'(\.mp3|\.ogg)', '', mp3FileName)

		checkTitleOnGoogle = gSuggDidYouMean(str(titleFromFile))
		if checkTitleOnGoogle:
			titleFromFile = checkTitleOnGoogle
			searchQuery = titleFromFile
		else:
			searchQuery = str(titleFromFile)

		searchQuery = re.sub(r'(audio|HQ|1080p|official|video)', '', searchQuery, re.IGNORECASE)



		#print "NO ARTIST OR TITLE TAGS!"
		#destination="OUTPUT_6_NO_TAGS/" + mp3FileName
		#makeTheDir("OUTPUT_6_NO_TAGS")
		#os.rename(source, destination )
		#return ''


	if 'TAG_IS_EMPTY' in (ipArtist,ipTitle,ipAlbumTitle,ipReleaseYear,ipGenre,ipCover):

		############ Probably drop this part
		if 'TAG_IS_EMPTY' in ipAlbumTitle:
			sQ3 = ''
		else:
			sQ3 = ipAlbumTitle
		###########



		print 'Go Get Info: ' + searchQuery
		if searchDiscogs(searchQuery):
			# if positive results are returned, exit out and return a result, this will enable addTagsToFile to start
			return "Cool!"

	else:
		print 'File OK: ' + ipArtist + " " + ipTitle
		print "MV FILE TO OUTPUT_2_ALREADY_GOOD"
		source="inputfiles/" + mp3FileName
		destination="OUTPUT_2_ALREADY_GOOD/" + mp3FileName
		makeTheDir("OUTPUT_2_ALREADY_GOOD")
		os.rename(source, destination )
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

	opArtist      = 'TAG_IS_EMPTY'
	opTitle       = 'TAG_IS_EMPTY'
	opAlbumTitle  = 'TAG_IS_EMPTY'
	opAlbumArtist = 'TAG_IS_EMPTY'
	opReleaseYear = 'TAG_IS_EMPTY'
	opGenre       = 'TAG_IS_EMPTY'
	opCover       = 'TAG_IS_EMPTY'

	discogs = discogs_client.Client('ExampleApplication/0.1', user_token="tLOqGxpsHNYovSMEvRsFXgtAfXKOfIBRwbhkiepw")

	results = discogs.search(searchQuery, type='release')
	results.pages
	1
	try:
		firstRelease = results[0]

	except IndexError:
		print "NO RESULTS"
		firstRelease = ''
		response = gSuggDidYouMean(str(searchQuery))
		print "GOOGLE SAYS: " + response

		if response and response != searchQuery:
			# Had to include this as a stray ' caused the response to match the query and cause an infinite loop
			#if response != searchQuery:
			checkArtist = gSuggDidYouMean(str(ipArtist))
			if checkArtist:
				ipArtist = 'TAG_IS_EMPTY'

			checkTitle = gSuggDidYouMean(str(ipTitle))
			if checkTitle:
				ipTitle = unicode(checkTitle).title()

			searchDiscogs(response)
			return ''
		else:
			print "NO RESULTS! SANITISING"
			sanitised = sanitiseString(searchQuery)
			if sanitised and sanitised != response:
				print "S: " + sanitised
				print "R: " + response
				print "SEARCHING WITH CLEAN STRING!"
				searchDiscogs(sanitised)
				return ''
			else:
				pass
			print "MV FILE TO OUTPUT_4_NO_RESULTS"
			source="inputfiles/" + mp3FileName
			destination="OUTPUT_4_NO_RESULTS/" + mp3FileName
			makeTheDir("OUTPUT_4_NO_RESULTS")
			os.rename(source, destination )
			# Do nothing more with this file
			firstRelease = ''
			return ''

	if firstRelease:
		try:
			print results[0].id
			masterRelease = discogs.master(results[0].id)

			try:				
				print "USING RELEASE"
				opAlbumTitle  = firstRelease.title
				artistInfo    = firstRelease.artists[0]
				opArtist      = artistInfo.name
				opReleaseYear = firstRelease.year
				opGenre       = firstRelease.styles[0]
				opCover       = firstRelease.images[0]['uri']

				tmpArtist     = re.sub(r'\&', 'And', opArtist)
				opAlbumTitle  = re.sub(r'\* - ', ' - ', opAlbumTitle)
				opAlbumTitle  = re.sub(r'^' + re.escape(opArtist) + ' - ', '', opAlbumTitle)
				opAlbumTitle  = re.sub(r'^' + re.escape(tmpArtist) + ' - ', '', opAlbumTitle)

			except :
				print "NO RELEASE or MISSING SOME FIELDS"
				try: 
					print "USING MASTER"
					discogsSearchOutput = getDiscogsResultsFromMaster(masterRelease)
					opAlbumTitle  = masterRelease.main_release.title
					artistInfo    = masterRelease.main_release.artists[0]
					opArtist      = re.sub(r' (\([0-9])\w+\)$', '', artistInfo.name)
					opReleaseYear = masterRelease.main_release.year
					opGenre       = masterRelease.main_release.styles[0]
					opCover       = masterRelease.main_release.images[0]['uri']
					source="inputfiles/" + mp3FileName
					destination="OUTPUT_7_MASTER_BUT_NO_RELEASE/" + mp3FileName
					makeTheDir("OUTPUT_7_MASTER_BUT_NO_RELEASE")
					os.rename(source, destination )
					return ''
				except:
					print "NO MASTER or MISSING SOME FIELDS"

			opArtist       = re.sub(r' \(([0-9])\)', '', artistInfo.name)
			opAlbumArtist  = opArtist

			if re.search(r'various|varios',opArtist, re.IGNORECASE):
				opAlbumArtist = "Various"

		except:
			print "WHOOPS"
			print "SOME RESULTS, BUT NOT GOOD ENOUGH"
			goCheckGoogle = gSuggDidYouMean(str(searchQuery))
			if goCheckGoogle:
				searchDiscogs (goCheckGoogle)
			else:

				print "MV FILE TO OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH"
				source="inputfiles/" + mp3FileName
				destination="OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH/" + mp3FileName
				makeTheDir("OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH")
				os.rename(source, destination )
				# Do nothing more with this file
			return ''

	if "TAG_IS_EMPTY" in (opArtist,opAlbumTitle,opAlbumArtist,opReleaseYear,opGenre,opCover):
		print "SOME RESULTS, BUT NOT GOOD ENOUGH"
		print "REALLY MV FILE TO OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH " + str(searchQuery)
		goCheckGoogle = gSuggDidYouMean(str(searchQuery))
		if goCheckGoogle:
			print "yiss " + str(goCheckGoogle)
			searchDiscogs (goCheckGoogle)
		else:
			source="inputfiles/" + mp3FileName
			destination="OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH/" + mp3FileName
			makeTheDir("OUTPUT_3_RESULTS_NOT_GOOD_ENOUGH")

			#checkTitleOnGoogle = gSuggDidYouMean(str(titleFromFile))

			os.rename(source, destination )
		return ''
	else:


		#print "OK"
		print "ALBUM: "  + opAlbumTitle
		print "ARTIST: " + opArtist
		print "ALBUM ARTIST: " + opAlbumArtist
		print "YEAR: "   + str(opReleaseYear)
		print "GENRE: "  + opGenre
		print "COVER: "  + opCover
		#print "hey!"
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

	if ipCover      == "TAG_IS_EMPTY":
		coverFile = urllib2.urlopen(opCover)
		with open(jpgTmp,'wb') as output:
			output.write(coverFile.read())


		pic = APIC(3, u'image/jpg', 3, u'Front cover', open(jpgTmp, 'rb').read())
		newTag.add(pic)

	if ipTitle == "TAG_IS_EMPTY" or titleFromFile:
		print "Adding ID3 ipTitle;",
		#opTitle = mp3FileName
		opTitle = unicode(mp3FileName).title()
		opTitle = re.sub(r'\.mp3', '', opTitle, re.IGNORECASE)
		opTitle = re.sub(r'\.ogg', '', opTitle, re.IGNORECASE)
		opTitle = re.sub(r'^' + re.escape(opArtist) , '', opTitle)
		opTitle = re.sub(r'^( |\-|\_)', '', opTitle)
		opTitle = re.sub(r'^( |\-|\_)', '', opTitle)
		
		#opTitle = "GOAT!"
		#opTitle       = re.sub(r'inputfiles/', '', useThisFile)
		newTag.add(TIT2(encoding=3, text=opTitle))


	if ipAlbumTitle       == "TAG_IS_EMPTY":
		print "Adding ID3 ipAlbumTitle;",
		newTag.add(TALB(encoding=3, text=opAlbumTitle))
	if ipAlbumArtist       == "TAG_IS_EMPTY":
		print "Adding ID3 ipAlbumArtist;",
		newTag.add(TPE2(encoding=3, text=opAlbumArtist))
	if ipGenre        == "TAG_IS_EMPTY":
		print "Adding ID3 ipGenre;",
		newTag.add(TCON(encoding=3, text=opGenre))
	if ipArtist       == "TAG_IS_EMPTY" or titleFromFile:
		print "Adding ID3 ipArtist;",
		newTag.add(TPE1(encoding=3, text=opArtist))
	if ipReleaseYear      == "TAG_IS_EMPTY":
		print "Adding ID3 ipReleaseYear;",
		newTag.add(TDRC(encoding=3, text=str(opReleaseYear)))

	newTag.save()
	source="inputfiles/" + mp3FileName
	destination="OUTPUT_1_PROCESSEDD/" + mp3FileName
	makeTheDir("OUTPUT_1_PROCESSEDD")
	os.rename(source, destination )


for subdir, dirs, files in os.walk('inputfiles'):
	for file in files:

		filepath = subdir + os.sep + file
		mp3FileName = file
		if filepath.endswith(".mp3"):
			getTagsFromFile(filepath)
			#pass
			#if getTagsFromFile(filepath):
		#		print "Insert!"
				#insertNewTags(filepath)

			print '\n'
