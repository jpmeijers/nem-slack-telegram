'''
Created on 26.09.2015

@author: root
'''
import telegram
import time


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
        except Exception, e:
            print str(e)
            return None

    def listen_to_telegram(self, queue):
        '''
        Queries Telegram for Updates and puts them into a queue.
        '''
        last_update = 0
        print 'Listening to Telegram'
        print self.bot.getMe()
        while True:
            try:
                updates = self.bot.getUpdates(offset=last_update + 1)
                for update in updates:
                    #print 'Received from telegram:', update
                    if update.message.photo:
                        update.message.text = self.download_file(update.message.photo[-1].file_id).file_path
                    if update.message.document:
                        update.message.text = self.download_file(update.message.document.file_id).file_path
                    #get avatar
                    avatar = self.download_avatar(update.message.from_user.id)
                    update.message.from_user.avatar = avatar
                    print 'Queued: ', update
                    queue.put(update)
                    last_update = update['update_id']
                time.sleep(1)
            except Exception, e:
                print 'Something went wrong - listening to telegram'
                # fuck it so it won't crash ever
                print str(e)
                time.sleep(5)

    def forward_to_telegram(self, queue):
        '''
        Takes a message from a queue and posts it to telegram.
        Messages are expected to look like as they come from slack
        '''
        print 'Ready to forward to Telegram'
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
                    print 'unknown slack channel: %s ' % update['channel']
                    continue
                message = '%s \n %s' % (username, update['text'])
                self.bot.sendMessage(chat_id=channel,
                                        text=message)
            except Exception, e:
                print 'Something went wrong - forwarding to telegram'
                # fuck it so it won't crash ever
                print str(e)
                time.sleep(5)
