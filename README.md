# nem-slack-telegram

__1. config.ini__  
To get this bridge between slack and telegram going you need to adapt a few things. 
You need to make a copy of config_template.ini and rename that copy to config.ini. 
Insert your API-keys into config.ini. 

__2. bridge.py__
In bridge.py you there is a variable called SLACK_CHANNEL_MATCHING. 
Change the channel to your own channels. The keys are slack channels, the values are telegram channels. 

__3. misc__
There are some lines in the modules that send to "pats-testing-range" which is a slack channel that i send some debugging messages to. You can comment that out, change the channel, it's not really an important thing, the bridge should work either way. 
