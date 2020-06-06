#!/usr/bin/env python
'''
Import Modules
'''
import sys
import time
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

            if(loglvl >= 2):
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

            if(loglvl >= 2):
              print("TWITTER BOT: Params {0}".format(params))

            bot.post('direct_messages/events/new', params=params)

            if (loglvl >= 2):
              print("TWITTER BOT: Message  sent-  {0}".format(message))

    def on_error(self, status_code, data):

        if (loglvl >= 0):
           print(status_filtercode)
        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        self.disconnect()

def sendTweet(tStr):
  '''
  Function to tweet a string
  '''
  bot = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

  bot.update_status(status=tStr)
  if (loglvl >= 2):
    print ("TWITTER BOT: Send tweet succesfully -  " + tStr)


def main():
  '''
  Main function
  '''
  try:
    randNum = randrange(100)

    '''
    Create Stream Object
    '''
    if (loglvl >= 2):
      print ("TWITTER BOT: Stream object created. ")
    stream = MyStreamer(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    stream.statuses.filter(track='@gafurmp')

  except TwythonError as err:
    if (loglvl >= 0):
      print("TWITTER BOT: Oops! Something went wrong!.  {0}".format(err))

  except TwythonAuthError as err:
    if (loglvl >= 0):
      print("TWITTER BOT: Oops! Authentication failed!.  {0}".format(err))

  except TwythonRateLimitError as err:
    if (loglvl >= 0):
      print("TWITTER BOT: Oops! Limit Reached!.  {0}".format(err))

  except RuntimeError as err:
    if (loglvl >= 0):
      print("TWITTER BOT: Oops! Something went wrong during runtime {0}".format(err))

  finally:
    if (loglvl >= 2):
       print("TWITTER BOT: main executed!")
    sleep(0.5)


if __name__=='__main__':
  main()
