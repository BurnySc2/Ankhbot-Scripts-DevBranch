#################
Info
#################

Description: Automatic Beting System for the Game StarCraft II
Created by: Brain - www.twitch.tv/wellbrained
Version: 1.1.2

#################
Variables in the Response Messages
#################

For more Informations about the variables you can use in the response Messages
check out the Link/File in the same Directory: "Overview - Usable Variables (opens Browser)"

################
Usage
################
Download the current Ankhbot version: https://www.ankhbot.com/download/

Download and install Python 2.7.13 since that's needed for AnkhBot and Scripting features: 
https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi 

Open AnkhBot and go to the "Scripts" tab in the bottom sidebar.
Click on the cogwheel in the top right and set your Python directory to the `Lib` folder where you installed Python 
(By default it should be `C:\Python27\Lib`).

Copy the script to `AnkhBotFolder\Twitch\Scripts\`

Go back to the `Scripts` tab in AnkhBot and rightclick the background and click "Reload Scripts".
The script should now appear in AnkhBot and you can configure your betting system script.

To enable overlays you need to click the `Insert API Key` on the contextmenu by rightclicking on the script in AnkhBot.

Don't forget to enable the checkbox "betting system active" and then the betting system should work for you!

###############
Version History
###############

1.1.2
  ~ Added dev options - testing overlay vs AI and multiple entries
  ~ Added Voting system (either without currency or with currency and a fixed amount)
  ~ Added ability to display percentages of amount of votes / amount of currency worth of bets  
  ~ Removed "Betting Enabled" because Ankhbot put in its own enabler

1.1.1:
  ~ Replaced "requests" with "urllib2"
  ~ Fixed some stuff

1.1.0:
  ~ Added Overlay System
	+ First Design: StarCraft II

1.0.0:
  ~ First Release version
