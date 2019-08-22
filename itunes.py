import xml.etree.ElementTree as ET
import operator
from collections import OrderedDict
import pprint
import datetime

def getTimeString(millis):
	days = millis // (1000 * 60 * 60 * 24)
	millis -= days * (1000 * 60 * 60 * 24)
	hours = millis // (1000 * 60 * 60)
	millis -= hours * (1000 * 60 * 60)
	minutes = millis // (1000 * 60)
	millis -= minutes * (1000 * 60)
	seconds = millis // 1000
	return "{} days, {} hours, {} minutes, {} seconds".format(days, hours, minutes, seconds)

def parseXML(xmlfile):
	songinfo = []
	tree = ET.parse(xmlfile)
	root = tree.getroot()
	test = root.findall("./dict/dict/dict")
	getfield = False
	for dic in test:
		song = {}
		field = ""
		for a in dic:
			if (a.tag == "key"):
				if (a.text == "Name" or a.text == "Artist" or a.text == "Album" or a.text == "Play Count" or a.text == "Total Time"):
					getfield = True
					field = a.text
					continue
			if (getfield):
				getfield = False
				song[field] = a.text
				field = ""
		songinfo.append(song)
	return songinfo

def mergeArtistInfo(songinfo):
	merged = {}
	for song in songinfo:
		artist = song['Artist']
		if (artist not in merged):
			merged[artist] = []
		del song['Artist']
		merged[artist].append(song)
	return merged

def aggregateStats(merged):
	aggregated = []
	for key, value in merged.items():
		totalArtistListenTime = 0
		totalArtistPlayCount = 0
		mostPlayedSong = {}
		mostPlayedSongCount = 0
		mostPlayedSongLength = 0
		highestCountSong = {}
		highestCountSongCount = 0
		for song in value:
			count = int(song.get("Play Count", 0))
			length = int(song.get("Total Time"))
			totalArtistPlayCount += count
			totalArtistListenTime += length * count
			if (count * length > mostPlayedSongCount * mostPlayedSongLength):
				mostPlayedSong = song
				mostPlayedSong["Total Listen Time (Human)"] = getTimeString(count * length)
				mostPlayedSongCount = count
				mostPlayedSongLength = length
			if (count > highestCountSongCount):
				highestCountSong = song
				highestCountSong["Total Listen Time (Human)"] = getTimeString(count * length)
				highestCountSongCount = count
		
		if (totalArtistPlayCount != 0):
			aggregated.append({"Artist": key, "Total Listen Time": totalArtistListenTime, "Total Listen Time (Human)": getTimeString(totalArtistListenTime), "Total Play Count": totalArtistPlayCount, "Most Played Song": mostPlayedSong, "Highest Count Song": highestCountSong})
	return aggregated

def getlistentime(elem):
	return elem['Total Listen Time']

songinfo = parseXML("Library.xml")
merged = mergeArtistInfo(songinfo)
aggregated = aggregateStats(merged)
sortedThing = sorted(aggregated, key=getlistentime, reverse=True)
pprint.PrettyPrinter(indent=4).pprint(sortedThing)