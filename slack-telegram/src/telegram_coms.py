'''
Created on 26.09.2015

@author: root
'''
import telegram
import time


def listen_to_telegram(token, queue):
    '''
    Queries Telegram for Updates and puts them into a queue.
    '''
    telegram_bot = telegram.Bot(token)
    last_update = 0
    print 'Listening to Telegram'
    while True:
        updates = telegram_bot.getUpdates(offset=last_update + 1)
        for update in updates:
            print 'Received from telegram:', update
            if update.message.chat.title == 'NEM::Red':
                queue.put(update)
                last_update = update['update_id']
        time.sleep(1)


def forward_to_telegram(token, queue):
    '''
    Takes a message from a queue and posts it to telegram.
    Messages are expected to look like as they come from slack
    '''
    telegram_bot = telegram.Bot(token)
    print 'Ready to forward to Telegram'
    while True:
        update = queue.get()
        username = update['user']['name']
        message = '%s \n %s' % (username, update['text'])
        telegram_bot.sendMessage(chat_id='-14284494',
                                text=message)
