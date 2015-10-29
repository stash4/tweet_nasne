# -*- coding: utf-8 -*-

import urllib2
import json
import time
import twitter
import twitterKeys

api = twitter.Api(
	twitterKeys.keys['consumerKey'],
	twitterKeys.keys['consumerSecret'],
	twitterKeys.keys['accessToken'],
	twitterKeys.keys['accessTokenSecret']
	)

nasne_ip = "192.168.10.30:64210"

# nasneのAPIを叩く
def getNasneStatus(nasne_ip):
	try:
		hddInfo = urllib2.urlopen("http://" + nasne_ip + "/status/HDDInfoGet?id=0")
		j_hddInfo = json.loads(hddInfo.read())
		hddUsage_Per = round((float(j_hddInfo['HDD']['usedVolumeSize']) / float(j_hddInfo['HDD']['totalVolumeSize'])) * 100, 2)
		hddFree_GB = round((float(j_hddInfo['HDD']['freeVolumeSize']) / 1024 / 1024 / 1024), 2)
		nasneStatuses = {"hddUsage": hddUsage_Per,
						"hddFree": hddFree_GB
						}
		return nasneStatuses
	except:
		time.sleep(10)

# UserTimeline取得ループ
since = 1		
while(True):
	try:
		myTimeline = api.GetUserTimeline(count=10,since_id=since)
		tweetNum = 0
		for tweet in myTimeline:
			if(tweetNum == 0):
				since = tweet.id
			print(tweet.text)
			if('nasne' in tweet.text):
				if('API' in tweet.text):
					ns = getNasneStatus(nasne_ip)
					content = "@stash_4 nasne status\n" + "HDD usage: " + str(ns['hddUsage']) + "%\n" + "Free space: " + str(ns['hddFree']) + "GB"
					api.PostUpdate(content.decode('utf-8'), in_reply_to_status_id=tweet.id)
			tweetNum += 1
		time.sleep(10)
	except:
		time.sleep(30)
