# -*- coding: utf-8 -*-
import tweepy, json, random, re, requests, urllib


CONSUMER_KEY = 'jQNHx6yU7lYWArC6yVtcILEAC'
CONSUMER_SECRET = 'jNrLSJoF64LTEqT3NINVPHBZPt0Lxj8Y5OdbYhQNY9pm9qWt6E'
ACCESS_KEY = '732646001752854528-y6T4zYOYeo9OHjfwnS3iIdeQum3gsLp'
ACCESS_SECRET = 'NOk1Xetk1WnjDw6xyQQtRjU56AsTq7C6A0FKfW8h910NM'


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

tag = '#ねこの写真ヘタクソ選手権'

def kat():
    tweets = tweepy.Cursor(api.search, q=tag).items(50)
    tweets_list = []
    for x in tweets:
        tweets_list.append(x)
    try:
        t = random.choice(tweets_list)
        tweet = json.dumps(t._json, indent=4)
        tj = json.loads(tweet)
        url = tj['entities']['media'][0]['media_url_https']
        ext = url.split('.')[-1]
        extreturn = 'kat.' + ext
        urllib.urlretrieve(url, extreturn)
        return extreturn
    except:
        pass


