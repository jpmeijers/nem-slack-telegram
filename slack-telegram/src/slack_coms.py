'''
Created on 26.09.2015

@author: root
'''
import time
import json
import re
import logging
from slackclient import SlackClient


class SlackManager():

    def __init__(self, token, channel_matching, emo_matching=None,
                 *args, **kwargs):
        self.bot = SlackClient(token)
        self.channel_matching = channel_matching
        self.emo_matching = emo_matching

    def _resolve_user(self, uid):
        user = json.loads(self.bot.api_call('users.info',
                                         user=uid))
        return user['user']

    def replace_emos(self, text):
        for i, j in self.emo_matching.iteritems():
            text = text.replace(i, j)
        return text

    def prep_message(self, update):
        try:
            #get user data
            user = self._resolve_user(update['user'])
            update['user'] = user  # user is a dict now

            #resolve mentionings
            marked_users = set([m.group(1) for m in
                                            re.finditer('<@([A-Z0-9]+)>',
                                                        update['text'])])
            for marked_user in marked_users:
                username = self._resolve_user(marked_user)['name']
                update['text'] = update['text'].replace(marked_user,
                                                        username)
            #replace emos
            update['text'] = self.replace_emos(update['text'])
        except Exception, e:
            logging.error(str(e))
        return update

    def listen_to_slack(self, queue):
        '''
        Queries Slack for Updates and puts them into a queue.
        '''
        while True:
            if self.bot.rtm_connect():
                logging.info('Listening to Slack')
                while True:
                    try:
                        updates = self.bot.rtm_read()
                        for update in updates:
                            #print 'Received from slack', update
                            if update.get('subtype') == 'bot_message':
                                #msg from a bot - move on
                                continue
                            if not update.get('text'):
                                #no text = move on
                                continue
                            else:
                                update = self.prep_message(update)
                                logging.debug('Queued: %s' % update)
                                queue.put(update)
                            time.sleep(1)
                    except Exception, e:
                        logging.error(str(e))
                        break
            else:
                logging.error('Failed to establish a connection to Slack!')

    def forward_to_slack(self, queue):
        '''
        Takes a message from a queue and posts it to slack.
        Messages are expected to be objects as returned from the
        Telegram API.
        '''
        logging.info('Ready to forward to Slack')
        while True:
            try:
                update = queue.get()
                try:
                    channel = self.channel_matching[update.message.chat.id]
                except KeyError:
                    logging.error('unknown telegram channel: %s ' % update.message.chat.id)
                    continue
                logging.debug(update.message.text)
                message = update.message.text.encode('utf-8')

                #resolve quotes
                if update.message.reply_to_message:
                    reply_to_message = update.message.reply_to_message.text.encode('utf-8')
                    reply_to_message = reply_to_message.replace('\n', '\n>')
                    message = '>%s:\n>%s\n%s' % (update.message.reply_to_message.from_user.username,
                                               reply_to_message,
                                               message)

                avatar = update.message.from_user.avatar
                # avatar = 'https://telegram.org/img/t_logo.png'
                #weird issue that makes slack display wrong icons so fuck it
                self.bot.api_call('chat.postMessage',
                                channel=channel,
                                text=message,
                                username=update.message.from_user.username,
                                icon_url=avatar
                                )
            except Exception, e:
                logging.error(str(e))
                time.sleep(5)

    def post_to_slack(self, message, user, channel):
        '''
        Another method to post to slack. Made id seperate so
        diagnostics will go through even if thread dies
        '''
        self.bot.api_call('chat.postMessage',
                        channel=channel,
                        text=message,
                        username=user)
