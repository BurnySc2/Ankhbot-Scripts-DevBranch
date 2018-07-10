#################
Info
#################
Description: Tweets when you are going live!
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.2.0


################
Step by Step installation
################
Step 1) 
- Enter the path to your default Python27 directory with python.exe (per default: 'C:/Python27/python.exe')
- Click the 'Install PIP Requests' button to install a necessary library

NOTE: In case you didn't install PIP with the Python installation follow this guide:
https://pip.pypa.io/en/stable/installing/
Or just install the Python27 again with the function enabled.

Step 2)
- Click the 'Register Twitter App' button
- Create a new app where you can fill in whatever you want. An example:

# Name: SL Chatbot - LiveTweet
# Description: SL Chatbot - LiveTweet
# Website: https://www.twitch.tv/<yourTwitchName>
# Callback URL: https://www.twitch.tv/<yourTwitchName>

Step 3)
After creation go to the 'Keys and Access Tokens' tab and press the button to create the Access information.
Copy paste the necessary four tokens into Chatbot:
# Consumer Key + Secret
# Access Token + Secret

With this you'll give Chatbot the permission to send out Tweets in your stead.


################
Usage
################
Download the current Streamlabs Chatbot version: https://streamlabs.com/chatbot

Download and install Python 2.7.13 since that's needed for Chatbot and the Script features: 
https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi 

Open the SL Chatbot and go to the "Scripts" tab in the left sidebar.
Click on the cogwheel in the top right and set your Python directory to the `Lib` folder where you installed Python 
(By default it should be `C:\Python27\Lib`).

Copy the scripts you want to use into the folder from the SL Chatbot. You can also use the Import function per button on the top right in the "Scripts" tab.
(By default it should be `C:\Users\<Username>\AppData\Roaming\AnkhHeart\AnkhBotR2\Twitch\Scripts`)

Go back to the `Scripts` tab in Chatbot and rightclick the background and click "Reload Scripts". 
Afterwards the list of installed scripts should appear and you can start configuring those.



###############
Version History
###############
1.2.0:
  ~ Way better error logging (detection if python path or keys were incorrectly entered)
  ~ Added logs when $game and $title could not be replaced
  ~ Logs for which user the tweet was posted
  ~ "Install pip requests" command window stays open after the installation finished (so errors can be tracked down if any occured)
  ~ Saves script status to file in case of Streamlabs Chatbot restart during the stream to prevent a new automatic tweet
  ~ Added a $preview variable for twitch users - contains a link to a preview image to the stream
  ~ (optional) sends a new tweet when the streamer started playing a different game (tweet on game change), added a new text file for this feature (tweetOnGameChange.txt)
  ~ (optional) sends new tweet when some time (30-300 minutes) has passed since the stream went live, added a new text file for this feature (tweetPeriodic.txt)
  ~ (optional) removal of last tweet sent by bot before sending new one
1.1.1:
  ~ Emojis are now supported
1.1.0:
  ~ Changed methods to support Chatbot .29+ versions
1.0.2:
  ~ Disabled send-tweet button when the script is not enabled
  ~ Attempt to fix unicode characters
1.0.1:
  ~ Fixed the usage of paths with spaces in it  
  ~ Trimming user informations now to prevent errors with spaces
1.0.0:
  ~ First Release version

###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
