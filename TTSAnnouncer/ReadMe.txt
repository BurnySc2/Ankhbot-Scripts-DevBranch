#################
Info
#################
Description: Text-to-Speech Announcer
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.1.2


#################
Setting up the TTS script
#################
Step 1) 
Click the "Save Settings" buttons in the TTS settings and go into the "Get a link for your Browser Source" section.
You have now the option to choose from either button:

___ Open the link in my browser ___
This will open a new tab in your default browser and the link will be the URL in this tab.
   
___ Whisper me the link per Twitch ___
The bot will whisper you the link on Twitch. 
NOTE: This will only work if you have a seperate Bot account and don't use the streamer account for both.

Step 2)
Copy the link and use it as URL for a Browser Source in OBS.
NOTE: If you don't want the actual overlay but just the announcer set the size of the source to 1x1.

Step 3)
Finished. You can now test the script by writing `!tts This is a test` in your console/chat.

Note regarding additional languages:
You see in front of each language the countrycode which is necessary to use after !tts.
Example: (DE) German.
Usage: !ttsde Das ist ein Test.


Caution: If your key is visible on stream, it may cause people to spam TTS (without using !tts <text> in chat). Simply generate a new "Unique Key" to fix this.

Useful tip:
If you don't want the TTS announcer to be active in specific scenes, edit the browser source in OBS and check "Shutdown source when not visible". 
Now the TTS won't be working in scenes where you don't have the TTS browser source active.


################
General Installation of Scripts
################
Download the current Streamlabs Chatbot version: https://streamlabs.com/chatbot

Download and install Python 2.7.13 since that's needed for Chatbot and the Script features: 
https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi 

Open the SL Chatbot and go to the "Scripts" tab in the left sidebar.
Click on the cogwheel in the top right and set your Python directory to the `Lib` folder where you installed Python 
(By default it should be `C:\Python27\Lib`).

Click the 'Import' button top right in the "Scripts" tab and select the .zip file you downloaded. It will automatically install the script and move the files into the correct directory.

Afterwards the list of scripts get reloaded and you can start configuring those.



###############
Version History
###############
1.1.2:
  ~ fixed a critical error with user permissions (when it was set to sub-only)
  ~ A minor faulty fix in error logging

1.1.1:
  ~ Added a response message when a message didnt pass the black word list filter
  ~ Permission for Moderators to use TTS is now seperated
  ~ Added Checkbox: Godmode for the streamer so all cooldowns and costs will be ignored
  ~ A huge bugfix for youtube streamers
  ~ Fixed when the list of black words ended with comma

1.1.0:
  ~ Changed methods to support Chatbot .29+ versions

1.0.4:
  ~ Added a button to generate your Unique Key and your OBS Browser Source Link

1.0.3:
  ~ No idea anymore

1.0.2:
  ~ Fixed a bug where an error occurs without saving first. 
  ~ Fixed a bug which happens when you leave the blacklist empty.

1.0.1:
  ~ First Release version


###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
