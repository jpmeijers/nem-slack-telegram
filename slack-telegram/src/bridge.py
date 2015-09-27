'''
Created on 26.09.2015

@author: root
'''
import Queue
import threading
import slack_coms
import telegram_coms
import time

SLACK_TOKEN = 'xoxb-11406663559-mTpyvwOxMSsE1pzTq5YoXyMO'
TELEGRAM_TOKEN = '131728076:AAGclALKrc3Talha48OkD2xx9R-EWwBgCcU'

'''Queues are used to pass information between Threads. Duh!'''
slack_output_queue = Queue.Queue()
#slack_forward_queue = Queue.Queue()
telegram_output_queue = Queue.Queue()
#telegram_forward_queue = Queue.Queue()


'''All threads are being created and started.'''
slack_listen_thread = threading.Thread(name='slack_listener',
                                       target=slack_coms.listen_to_slack,
                                       args=(SLACK_TOKEN, slack_output_queue))
slack_listen_thread.setDaemon(True)
slack_listen_thread.start()

telegram_listen_thread = threading.Thread(name='telegram_listener',
                                       target=telegram_coms.listen_to_telegram,
                                       args=(TELEGRAM_TOKEN,
                                             telegram_output_queue))
telegram_listen_thread.setDaemon(True)
telegram_listen_thread.start()

slack_forward_thread = threading.Thread(name='slack_forwarder',
                                       target=slack_coms.forward_to_slack,
                                       args=(SLACK_TOKEN,
                                             telegram_output_queue))

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
        message = 'Running Threads: ' + ', '.join(thread.name for
                                                 thread in
                                                 threading.enumerate())
        slack_coms.post_to_slack(SLACK_TOKEN, message, 'diagnostics',
                                 'pats-testing-range')
        time.sleep(60 * 30)
