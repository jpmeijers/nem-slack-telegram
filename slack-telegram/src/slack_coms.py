'''
Created on 26.09.2015

@author: root
'''
import time
import json
import re
from slackclient import SlackClient

CHANNEL_MATCHING = {-14284494: 'nem_red'}


def resolve_user(bot, uid):
    user = json.loads(bot.api_call('users.info',
                                     user=uid))
    return user['user']


def prep_message(bot, update):
    try:
        #resolve mentionings
        user = resolve_user(bot, update['user'])
        marked_users = set([m.group(1) for m in
                                        re.finditer('<@([A-Z0-9]+)>',
                                                    update['text'])])
        for marked_user in marked_users:
            username = resolve_user(bot, marked_user)['name']
            update['text'] = update['text'].replace(marked_user,
                                                                    username)
        update['user'] = user
        #replace emots
        update['text'] = update['text'].replace(':stuck_out_tongue:', ':P').replace(':smile:', ':)')
    except:
        pass  # fuck anything
    return update


def listen_to_slack(token, queue):
    '''
    Queries Slack for Updates and puts them into a queue.
    '''
    slack = SlackClient(token)
    if slack.rtm_connect():
        print 'Listening to Slack'
        while True:
            try:
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
                        update = prep_message(slack, update)
                        queue.put(update)
                    time.sleep(1)
            except Exception, e:
                print 'Something went wrong - listening to Slack'  # fuck it so it won't crash ever
                print str(e)
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
        try:
            update = queue.get()
            channel = ''
            if update.message.chat.title == 'NEM::Red':
                channel = 'nem_red'
            if update.message.chat.title == 'NEM::Tech':
                channel = 'nem_tech'

            message = update.message.text.encode('utf-8')
            if update.message.reply_to_message:
                reply_to_message = update.message.reply_to_message.text.encode('utf-8')
                reply_to_message = reply_to_message.replace('\n', '\n>')
                message = '>%s:\n>%s\n%s' % (update.message.reply_to_message.from_user.username,
                                           reply_to_message,
                                           message)
            slack.api_call('chat.postMessage',
                            channel=channel,
                            text=message,
                            username=update.message.from_user.username, icon_url=update.message.from_user.avatar)
        except Exception, e:
            print 'Something went wrong - forwarding to Slack'  # fuck it so it won't crash ever
            print str(e)


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
