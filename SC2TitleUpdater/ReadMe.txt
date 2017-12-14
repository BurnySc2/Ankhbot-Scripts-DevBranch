#################
Info
#################

Description: Automatic Title Updater for the Game StarCraft II
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.0.1


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

To get the client ID and oauth:

To get a client ID, log in to your twitch and go to https://www.twitch.tv/kraken/oauth2/clients/new
Create a new twitch application like described here (50 seconds into the video): https://youtu.be/lmNM_I_ER-o?t=50s

After you created the app you'll receive a client ID and replace this ID with the "CLIENTID" in the url below and open it in your browser:
https://api.twitch.tv/kraken/oauth2/authorize?response_type=token&client_id=CLIENTID&redirect_uri=http://localhost&scope=channel_editor&scope=user_read+channel_editor

After you hit "Authorize" you get redirected to a blank page. The URL should look like this:
http://localhost/#access_token=2x0n6sdfldf934xi&scope=user_read+channel_editor

The "oauth" is the stuff after "access_token=" until it's at the "&scope". In this case the "oauth" would be: "2x0n6sdfldf934xi"

Don't forget to enable the checkbox "Enable Stream Title Changes" and then the title updater should work for you!

###############
Version History
###############

1.0.1:
  ~ using regex to get MMR from RankedFTW now
  ~ renamed "StarCraft Accounts" to "player names"
  ~ also added buttons that take you directly to your app creation in twitch

1.0.0:
  ~ First Release version

###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.