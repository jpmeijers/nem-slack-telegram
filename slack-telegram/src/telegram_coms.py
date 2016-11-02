'''
Created on 26.09.2015

@author: root
'''
import telegram
import time
import logging
import json


class TelegramManager():

    def __init__(self, token, channel_matching, *args, **kwargs):
        self.bot = telegram.Bot(token)
        self.channel_matching = channel_matching

    def download_file(self, file_id):
        return self.bot.getFile(file_id=file_id)

    def download_avatar(self, uid):
        try:
            file_id = self.bot.getUserProfilePhotos(uid).photos[0][0].file_id
            return self.download_file(file_id).file_path
        except IndexError:
            logging.info("no avatar found")
        except Exception, e:
            logging.error(str(e))
            return None

    def listen_to_telegram(self, queue):
        '''
        Queries Telegram for Updates and puts them into a queue.
        '''
        logging.info('Listening to Telegram')
        logging.info(self.bot.getMe())
        last_update = 0
        while True:
            time.sleep(1)
            try:
                updates = self.bot.getUpdates(offset=last_update + 1)
                for update in updates:
                    if not update.message:
                        continue
                    if update.message.photo:
                        update.message.text = self.download_file(update.message.photo[-1].file_id).file_path
                    if update.message.document:
                        update.message.text = self.download_file(update.message.document.file_id).file_path
                    #get avatar
                    avatar = self.download_avatar(update.message.from_user.id)
                    update.message.from_user.avatar = avatar
                    logging.debug('Queued: %s' % update)
                    queue.put(update)
                    last_update = update['update_id']
                time.sleep(1)
            except Exception, e:
                logging.error(str(e))
                time.sleep(5)

    def forward_to_telegram(self, queue):
        '''
        Takes a message from a queue and posts it to telegram.
        Messages are expected to look like as they come from slack
        '''
        logging.info('Ready to forward to Telegram')
        while True:
            try:
                update = queue.get()
                try:
                    username = update['user']['name']
                except KeyError:
                    username = 'slacker'
                try:
                    channel = self.channel_matching[update['channel']]
                except KeyError:
                    logging.error('unknown slack channel: %s ' % update['channel'])
                    continue
                message = '*%s*\n%s' % (username, update['text'])
                self.bot.sendMessage(chat_id=channel,
                                        text=message,
                                        parse_mode="Markdown")
            except Exception, e:
                logging.error(str(e))
                time.sleep(5)
