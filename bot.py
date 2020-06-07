#!/usr/bin/env python
'''
Import Modules
'''
import sys
import os
import time
from threading import Thread
from time import sleep
from twython import Twython
from random import random
from random import randrange
from keys import *
from twython import TwythonStreamer
from twython import TwythonError
from twython import TwythonRateLimitError
from twython import TwythonAuthError
import json
from config import *
from datetime import datetime, timedelta
from threading import Timer

'''
Global Constants
'''

'''
Global Variables
'''

'''
Twitter Developer Datas
'''
# your twitter consumer and access information goes here
CONSUMER_KEY = keys['apiKey']
CONSUMER_SECRET = keys['apiSecret']
ACCESS_TOKEN = keys['accessToken']
ACCESS_TOKEN_SECRET = keys['accessTokenSecret']

class MyStreamer(TwythonStreamer):

    def on_success(self, data):

        if 'text' in data:
            '''
            Create Twitter Object
            '''
            bot = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

            '''
            Get user name and tweet details
            '''
            tweet = str(data['text'])
            user = str(data['user']['screen_name'])
            response = bot.lookup_user(screen_name=user)
            recipient_id = response[0]['id']

            bot.create_favorite(id = data['id'])

            if(LOGLVL >= 2):
              print("TWITTER BOT: recipient_id {0}".format(recipient_id))

    def on_error(self, status_code, data):

        if (LOGLVL >= 0):
           print(status_filtercode)
        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        self.disconnect()

def sendTweet(message):
   '''
   Function to tweet a string
   '''
   bot = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

   bot.update_status(status=message)
   if (LOGLVL >= 2):
     print ("TWITTER BOT: Send tweet succesfully -  " + message)

def random_line(fileName, default=None):
    '''
    Redds a random line from a file
    '''
    line = default
    for i, randomline in enumerate(fileName, start=1):
        if randrange(i) == 0:  # random int [0..i)
            line = randomline
    return line

def handleTweetMentions():
  '''
  Thread to handle streaming interfaces - to check mentions and repkly with a direct message
  '''
  try:
    '''
    Create Stream Object
    '''
    if (LOGLVL >= 2):
      print ("TWITTER BOT: Stream object created. ")
    stream = MyStreamer(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    '''
    Check for mentions
    '''
    stream.statuses.filter(track='@gafurmp')

  except TwythonError as err:
    if (LOGLVL >= 0):
      print("TWITTER BOT: Oops! Something went wrong!.  {0}".format(err))

  except TwythonAuthError as err:
    if (LOGLVL >= 0):
      print("TWITTER BOT: Oops! Authentication failed!.  {0}".format(err))

  except TwythonRateLimitError as err:
    if (LOGLVL >= 0):
      print("TWITTER BOT: Oops! Limit Reached!.  {0}".format(err))

  except RuntimeError as err:
    if (LOGLVL >= 0):
      print("TWITTER BOT: Oops! Something went wrong during runtime {0}".format(err))

  finally:
    if (LOGLVL >= 2):
       print("TWITTER BOT: handleTweetMentions executed!")
    sleep(0.5)

def randomTweet():

  while True:
    try:
      '''
      Random Quote Tweet
      '''
      startTime = datetime.today()
      nextTweet = startTime.replace(day = startTime.day, hour = RANDOM_TWEET_HOUR, minute = RANDOM_TWEET_MINUTE, second = RANDOM_TWEET_SEC, microsecond = RANDOM_TWEET_MSEC) + timedelta(days=RANDOM_TWEET_DAYS)
      deltaTime = nextTweet - startTime
      sleepTime = deltaTime.total_seconds()

      with open(os.path.join(os.path.dirname(__file__), RANDOM_TWEET_TXT_FILE)) as file:
        line =  random_line(file)
        sendTweet(line)

        if(LOGLVL >= 2):
          print("TWITTER BOT: random quote at {0}: ".format(startTime) + line)

    except OSError as err:
      if(LOGLVL >= 0):
        print("TWITTER BOT: Oops! Something went wrong! {0}".format(err))

    finally:
      if (LOGLVL >= 2):
         print("TWITTER BOT: randomTweet send!")
      sleep(sleepTime)

def createDirMsgAndSent(message, recipient_id):
  '''
  Function creates and send a direct message
  '''
  bot = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

  '''
  Set Params
  '''
  params = {
    "event": {
       "type": "message_create",
       "message_create": {
         "target": {
           "recipient_id": str(recipient_id),
           },
         "message_data": {
            "text": message,
            }
         }
       }
  }

  params = json.dumps(params)

  if(LOGLVL >= 2):
    print("TWITTER BOT: Params {0}".format(params))

  bot.post('direct_messages/events/new', params=params)

  if (LOGLVL >= 2):
    print("TWITTER BOT: Message  sent-  {0}".format(message))

def replyDirectMsg():
   '''
   Reply to incoming direct messages
   '''
   id = []
   bot = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

   while True:
     try:
       response = bot.get_direct_messages(count = 1)
       if (response['events'][0]['id'] not in id):
         if(response['events'][0]['message_create']['sender_id'] != TWITTER_SENDER_ID):
           if(LOGLVL >= 2):
             print("TWITTER BOT: DM response {0}".format(response))
           id.append(response['events'][0]['id'])
           message = "Hi, This is an automated reply dated. I will get back to you asap!"
           createDirMsgAndSent(message, response['events'][0]['message_create']['sender_id'])
       else:
         if(LOGLVL >= 2):
           print("TWITTER BOT: DM ID {0} already replied.".format(response['events'][0]['id']))
     except:
       if(LOGLVL >= 0):
          print("TWITTER BOT: Unexpected Error", sys.exc_info()[0])
     finally:
       if(LOGLVL >= 2):
         print("TWITTER BOT: Executed replyDirectMsg thread")
       sleep(DM_POLL_FREQ_IN_HOUR * 60 * 60)

def main():
  '''
  Main function
  '''

  '''
  Start Threads
  '''
  handleTweetThread = Thread(target=handleTweetMentions)
  handleTweetThread.start()

  randomTweetThread = Thread(target=randomTweet)
  randomTweetThread.start()

  replyDirMsgThread = Thread(target=replyDirectMsg)
  replyDirMsgThread.start()

  '''
  End of execution... Join threads
  '''
  handleTweetThread.join()
  randomTweetThread.join()
  replyDirMsgThread.join()

if __name__=='__main__':
  main()
  #done
