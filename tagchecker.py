#!/usr/bin/python
# -*- coding: utf-8 -*-
# import discogs_client
import os
import re

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC, APIC

import pprint


#from pathlib import Path

# import io
# import gzip
# import sys
# import urllib

# from bs4 import BeautifulSoup
# #from StringIO import StringIO
# from io import StringIO

from mutagen import File
# import sys

#reload(sys)
#sys.setdefaultencoding('utf8')

inputFileDir  = 'inputfiles'
mp3FileName   = ''
titleFromFile = ''
guessTags     = ''

def moveTheFile(sourceFileName,destinationFolder):
	global mp3FileName
	print ('\n')
	print ("Moving " + sourceFileName + " to " + destinationFolder)
	sourceFile = inputFileDir + '/' + sourceFileName
	try: 
		os.makedirs(destinationFolder)
	except OSError:
		if not os.path.isdir(destinationFolder):
			os.makedirs(destinationFolder)
			raise
	destinationFile = destinationFolder + '/' + mp3FileName
	if os.path.isfile('destinationFile'):
		destinationFile = destinationFile + '_1'

	os.rename(sourceFile, destinationFile)
	print ('#################################')
	print ('\n')
	return ''


def checkForJunkEntry(tagToCheck):
	if re.match(r'^(unknown|na|n\/A|none|null|varios|various|various artists|varios artists|\ )$', tagToCheck, re.IGNORECASE):
		print ("JUNK TAG: " + tagToCheck)
		tagToCheck = 'TAG_IS_EMPTY'
	return tagToCheck


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

	# print (EasyID3.valid_keys.keys())
	# pprint.pprint(EasyID3.valid_keys.keys())

	#mp3info = str(mp3info, 'utf-8')

	#print (fileName)
	#print ("Filename: ") + (fileName) + (' ') + (mp3info)
	print ("Filename: " + fileName + ' ' )#+ mp3info)

###### Yo Dawg
	def checkTag(varName,tagName):
		try:
			varName = mp3info[tagName][0]
			varName = checkForJunkEntry(varName)
		except KeyError:
			varName = 'TAG_IS_EMPTY'
		return varName
######


	ipAlbumTitle  = checkTag('ipAlbumTitle','album')
	ipAlbumArtist = checkTag('ipAlbumArtist','albumartist')
	ipGenre       = checkTag('ipGenre','genre')
	ipArtist      = checkTag('ipArtist','artist')
	ipTitle       = checkTag('ipTitle','title')

	if checkTag('ipReleaseYear','date'):
		ipReleaseYear = checkTag('ipReleaseYear','date')[:4]
		print ('ipReleaseYear: ' + ipReleaseYear)
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

	# sQ1 = ipArtist
	# sQ2 = ipTitle
	
	# if sQ1 == 'TAG_IS_EMPTY':
	# 	sQ1 = ''

	# if sQ2 == 'TAG_IS_EMPTY':
	# 	sQ2 = ''

	# searchQuery = sQ1 + ' ' + sQ2

	# if searchQuery == ' ':
	# 	print ("No Artist or Title Tags! Taking a guess at them based on filename")
	# 	titleFromFile = sanitiseString(mp3FileName,1)
	# 	#artistFromFile = sanitiseString(mp3FileName,1)

	# 	checkTitleOnGoogle = gSuggDidYouMean(str(titleFromFile))
	# 	if checkTitleOnGoogle and checkTitleOnGoogle != "ATTRIBUTE_ERROR":
	# 		titleFromFile = checkTitleOnGoogle
	# 	sQ1 = str(titleFromFile)

	#tagsToCheck = [ipArtist,ipTitle,ipAlbumTitle,ipReleaseYear,ipGenre,ipCover]
	tagsToCheck = {'ipArtist': ipArtist,'ipTitle': ipTitle,'ipAlbumTitle': ipAlbumTitle,'ipReleaseYear': ipReleaseYear,'ipGenre': ipGenre,'ipCover': ipCover}
	
	for tagKey, tagValue in tagsToCheck.items():
	#for tagOla in tagsToCheck:
		if 'TAG_IS_EMPTY' in tagValue:
	#if 'TAG_IS_EMPTY' in (ipArtist,ipTitle,ipAlbumTitle,ipReleaseYear,ipGenre,ipCover):
        
			print ('Missing something: ' + tagKey )

			moveTheFile(mp3FileName,"OUTPUT_1_NEEDS_MORE_WORK_" + tagKey )
			break
			# print ('Go Get Info: ' + sQ1 + " " + sQ2)
			# if searchDiscogs(sQ1,sQ2):
			# 	# if positive results are returned, exit out and return a result, this will enable addTagsToFile to start
			# 	return "Cool!"
		else:
			continue
		# else:
		# 	print ("")
		# 	print ("Tag OK: " + tagKey + tagValue)
		break

	#print(mp3FileName)
	#if ( os.path.isfile(mp3FileName)):
	try:
		moveTheFile(mp3FileName,'OUTPUT_2_ALREADY_GOOD')
		print ("File OK: " + ipArtist + " " + ipTitle),
	#else:
	except:
		print ("File MOVED: " + mp3FileName)

	# print ("File OK: " + ipArtist + " " + ipTitle),
	# moveTheFile(mp3FileName,'OUTPUT_2_ALREADY_GOOD')
	return ''


######
for subdir, dirs, files in os.walk(inputFileDir):
	for file in files:

		filepath = subdir + os.sep + file
		print (filepath)#debug
		mp3FileName = file
		if re.search(r'mp3$', filepath, re.IGNORECASE):
			getTagsFromFile(filepath)
