# -*- coding: utf-8 -*-

import json
import re
import time
import twitter
import twitterKeys
import urllib2

api = twitter.Api(twitterKeys.keys['consumerKey'],
	  			  twitterKeys.keys['consumerSecret'],
				  twitterKeys.keys['accessToken'],
				  twitterKeys.keys['accessTokenSecret']
				 )

nasne_ip = "192.168.10.30"
searchPattern = r"nasne"

def getNasneStatus(nasne_ip):
	try:
		apiAddr = "http://" + nasne_ip + ":64210/status/"
		
		hddInfo = urllib2.urlopen(apiAddr + "HDDInfoGet?id=0")
		chInfo = urllib2.urlopen(apiAddr + "boxStatusListGet")
		
		j_hddInfo = json.loads(hddInfo.read())
		j_chInfo = json.loads(chInfo.read())
		
		hddUsage_Per = round((float(j_hddInfo['HDD']['usedVolumeSize']) / float(j_hddInfo['HDD']['totalVolumeSize'])) * 100, 2)
		hddFree_GB = round((float(j_hddInfo['HDD']['freeVolumeSize']) / 1024 / 1024 / 1024), 2)
		
		if j_chInfo['tvTimerInfoStatus']['nowId'] == "":
			recChannel = ""
			recTitle = ""
			recDescription = ""
		else:
			recInfo = urllib2.urlopen(apiAddr +
									  "channelInfoGet2?networkId="+ j_chInfo['tuningStatus']['networkId'] + 
									  "&transportStreamId=" + j_chInfo['tuningStatus']['transportStreamId'] +
									  "&serviceId=" + j_chInfo['tuningStatus']['serviceId'] +
									  "&withDescriptionLong=0"
									 )
			j_recInfo = json.loads(recInfo.read())
			recChannel = j_recInfo['channel']['tsName']
			recTitle = j_recInfo['channel']['title']
			recDescription = j_recInfo['channel']['description']
			
		nasneStatus = {"hddUsage"	: hddUsage_Per,
					   "hddFree"	: hddFree_GB,
					   "channel"	: recChannel,
					   "title"		: recTitle,
					   "description": recDescription
					  }
		return nasneStatus
	
	except:
		time.sleep(10)


if __name__ == '__main__':
	# UserTimeline取得ループ
	since = 1		
	while(True):
		try:
			myTimeline = api.GetUserTimeline(count=10,since_id=since)
			
			tweetNum = 0
			for tweet in myTimeline:
				if tweetNum == 0 :
					since = tweet.id
				
				if re.search(searchPattern, tweet.text):
					ns = getNasneStatus(nasne_ip)
					
					tweetHdd = u"@stash_4\nHDD_Status\nHDD usage: " + unicode(ns['hddUsage']) + u"%\nFree space: " + unicode(ns['hddFree']) + u"GB"
					api.PostUpdate(tweetHdd, in_reply_to_status_id=tweet.id)
					
					tweetRec = u"@stash_4\nRecording_Status\n"
					if ns['channel'] == "":
						tweetRec = tweetRec + u"The program isn't being recorded."
					else:
						tweetRec = tweetRec + u"The following program is being recorded.\nChannel: " + unicode(ns['channel']) + u"\nTitle:" + unicode(ns['title']) + u"\nDescription" + unicode(ns['description'])
					time.sleep(5)
					api.PostUpdate(tweetRec, in_reply_to_status_id=tweet.id)
				
				tweetNum += 1
		
			# API制限回避
			time.sleep(10)
		
		except:
			time.sleep(20)
