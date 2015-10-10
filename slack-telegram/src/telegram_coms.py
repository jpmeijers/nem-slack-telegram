'''
Created on 26.09.2015

@author: root
'''
import telegram
import time


def download_file(bot, file_id):
    return bot.getFile(file_id=file_id)


def download_avatar(bot, uid):
    try:
        file_id = bot.getUserProfilePhotos(uid).photos[0][0].file_id
        return download_file(bot, file_id).file_path
    except:
        return None


def listen_to_telegram(token, queue):
    '''
    Queries Telegram for Updates and puts them into a queue.
    '''
    telegram_bot = telegram.Bot(token)
    last_update = 0
    print 'Listening to Telegram'
    print telegram_bot.getMe()
    while True:
        try:
            updates = telegram_bot.getUpdates(offset=last_update + 1)
            for update in updates:
                print 'Received from telegram:', update
                if update.message.photo:
                    print 'RECEIVED PHOTO!'
                    update.message.text = download_file(telegram_bot,
                                                      update.message.photo[-1].file_id).file_path
                #get avatar
                avatar = download_avatar(telegram_bot,
                                         update.message.from_user.id)
                update.message.from_user.avatar = avatar
                queue.put(update)
                last_update = update['update_id']
            time.sleep(1)
        except Exception, e:
            print 'Something went wrong - listening to telegram'  # fuck it so it won't crash ever
            print str(e)
            time.sleep(5)


def forward_to_telegram(token, queue):
    '''
    Takes a message from a queue and posts it to telegram.
    Messages are expected to look like as they come from slack
    '''
    telegram_bot = telegram.Bot(token)
    print 'Ready to forward to Telegram'
    while True:
        try:
            update = queue.get()
            try:
                username = update['user']['name']
            except KeyError:
                username = 'slacker'
            channel = '-14284494'  # id for NEM::Red as default
            if update['channel'] == 'G0BCJ6A11':  # id for NEM::Tech
                channel = '-23053030'
            if update['channel'] == 'G0C7PQQ5V':  # id for NEM::Mobile
                channel = '-23053030'
            message = '%s \n %s' % (username, update['text'])
            telegram_bot.sendMessage(chat_id=channel,
                                    text=message)
        except Exception, e:
            print 'Something went wrong - forwarding to telegram'  # fuck it so it won't crash ever
            print str(e)
            time.sleep(5)
