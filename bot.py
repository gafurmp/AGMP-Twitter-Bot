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
from keys import keys
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

            if(LOGLVL >= 2):
              print("TWITTER BOT: recipient_id {0}".format(recipient_id))

            '''
            Define message
            '''
            message = "Hi, This is an automated reply dated " + data['created_at'] + ". I will get back to you asap!"

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
      nextTweet = startTime.replace(day = startTime.day, hour = RANDOM_TWEET_HOUR, minute = RANDOM_TWEET_MINUTE, second = RANDOM_TWEET_SEC, microsecond = RANDOM_TWEET_MSEC) + timedelta(days=1)
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

  '''
  End of execution... Join threads
  '''
  handleTweetThread.join()
  randomTweetThread.join()

if __name__=='__main__':
  main()
  #done
