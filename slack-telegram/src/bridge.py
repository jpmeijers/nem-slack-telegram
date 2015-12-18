'''
Created on 26.09.2015

@author: root
'''
import Queue
import threading
from slack_coms import SlackManager
import telegram_coms
import time
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read("config.ini")

SLACK_TOKEN = Config.get('Token', 'Slack')
TELEGRAM_TOKEN = Config.get('Token', 'Telegram')

slack = SlackManager(SLACK_TOKEN)

'''Queues are used to pass information between Threads. Duh!'''
slack_output_queue = Queue.Queue()
telegram_output_queue = Queue.Queue()


'''All threads are being created and started.'''
slack_listen_thread = threading.Thread(name='slack_listener',
                                       target=slack.listen_to_slack,
                                       args=(slack_output_queue,))
slack_listen_thread.setDaemon(True)
slack_listen_thread.start()

telegram_listen_thread = threading.Thread(name='telegram_listener',
                                       target=telegram_coms.listen_to_telegram,
                                       args=(TELEGRAM_TOKEN,
                                             telegram_output_queue))
telegram_listen_thread.setDaemon(True)
telegram_listen_thread.start()

slack_forward_thread = threading.Thread(name='slack_forwarder',
                                       target=slack.forward_to_slack,
                                       args=(telegram_output_queue, ))

slack_forward_thread.setDaemon(True)
slack_forward_thread.start()

telegram_forward_thread = threading.Thread(name='telegram_forwarder',
                                    target=telegram_coms.forward_to_telegram,
                                    args=(TELEGRAM_TOKEN,
                                          slack_output_queue))

telegram_forward_thread.setDaemon(True)
telegram_forward_thread.start()

if __name__ == '__main__':
    while True:
        try:
            message = 'Running Threads: ' + ', '.join(thread.name for
                                                     thread in
                                                     threading.enumerate())
            slack.post_to_slack(message, 'diagnostics',
                                     'pats-testing-range')
            time.sleep(60 * 30)
        except KeyboardInterrupt:
            raise
        #except:
            #print 'Something went wrong'  # fuck it so it won't crash ever
