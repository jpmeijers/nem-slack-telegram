'''
Created on 26.09.2015

@author: root
'''
import time
import json
from slackclient import SlackClient


def listen_to_slack(token, queue):
    '''
    Queries Slack for Updates and puts them into a queue.
    '''
    slack = SlackClient(token)
    if slack.rtm_connect():
        print 'Listening to Slack'
        while True:
            updates = slack.rtm_read()
            for update in updates:
                print 'Received from slack', update
                if update.get('subtype') == 'bot_message':
                    #msg from a bot - move on
                    continue
                if not update.get('text'):
                    #no text = move on
                    continue
                else:
                    #resolve user
                    user = json.loads(slack.api_call('users.info',
                                     user=update['user']))
                    update['user'] = user['user']
                    queue.put(update)
                time.sleep(1)
    else:
        print 'Failed to establish a connection to Slack!'


def forward_to_slack(token, queue):
    '''
    Takes a message from a queue and posts it to slack.
    Messages are expected to be objects as returned from the
    Telegram API.
    '''
    slack = SlackClient(token)
    print 'Ready to forward to Slack'
    while True:
        update = queue.get()
        slack.api_call('chat.postMessage',
                        channel='nem_red',
                        text=update.message.text.encode('utf-8'),
                        username=update.message.from_user.username)


def post_to_slack(token, message, user, channel):
    '''
    Another method to post to slack. Made id seperate so
    diagnostics will go through even if thread dies
    '''
    slack = SlackClient(token)
    slack.api_call('chat.postMessage',
                    channel=channel,
                    text=message,
                    username=user)
