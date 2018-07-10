#################
Info
#################
Description: Automatic Twitch Title & Overlay Files for the Game StarCraft II
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 2.0.5


################
Usage of SC2 MatchInfo - Twitch Title
################
If you want the script be able to update and change your stream title on Twitch you need to go to the "Configuration" section of the menu on the right side and click the "Get oAuth Token" button which will open a tab in your default browser. 

Click the "Generate oAuth Token" button there - Authorize the script and a textfield will appear above the button with your token in it. Copy paste that token into the "Twitch oAuth Token" field in the menu and save the settings.

Now you can type in the fields in the "Twitch Title Changer" section on how the stream titles should look like in each seperate status of your game and use variables in them which will be replaced with live data. For examples check the tooltips on the fields and a full overview of usable variables click the "Overview of all variables" button in the "Configuration section".
If you leave the fields empty it will do nothing.

Don't forget to enable the checkbox "Enable Stream Title Changes" and then the title updater should work for you!


################
Usage of SC2 MatchInfo - Overlay
################
For the overlay usage you'll have multiple textfiles in the "Overlay" sub folder from this script which you can use.
Variables like "$p2name" will be replaced in those files with the live data coming from the game and http://sc2unmasked.com so you can show on stream against who you're playing, his race and MMR. 

Three textfiles for each field in the "Overlay file - On Change" section and one textfile per "Overlay file - Change On Scene" so five in total.

A quick explanation on the differences between those and how variables work:

As you saw we have several variables implemented in this script: $p1name, $p1race, $p1mmr, etc.
$p1 (Player 1) is per default the streamer, your account - while $p2 (Player 2) is the opponent.

Those variables will be replaced with data from the game and http://sc2unmasked.com and the only difference is the moment when it will be replaced in the "On Change" and "Change On Scene" textfiles. To make it more clear there are also examples for each type.

___ Textfiles - On Change ___
Replaces the current info as soon as new infos are available (New opponent, etc.).

Example: You put "$p2name" in a field.
- You have a new game vs. PlayerXY and hence the textfile will contain PlayerXY.
- Afterwards you're back into the menu and it still shows PlayerXY.
- Now you're in a new game and the opponent is PlayerXXX. Now it will change from PlayerXY to PlayerXXX.


___ Textfiles - Change On Scene ___
Replaces the current info when you switch to a new scene in StarCraft II itself (In game, In Menu, In Replay, etc.).

Example: 
Field "On Scene - In Menu" contains "$p1mmr $p1race"
Field "On Scene - In Game" contains "$p1mmr $p1race playing against $p2name"

- You're in the menu and the textfile contains "4000 Zerg".
- You have a new game vs. PlayerXY and hence the textfile will contain "4000 Zerg playing against PlayerXY".
- You won the game and you're back in the menu. The textfile shows "4050 Zerg" (because you gained 50 MMR with this game).


#################
Setting up Dual PC usage
#################
Go to your "Blizzard Battle.Net Launcher" and then "Options > Game Settings". 
Scroll down until you are at the "StarCraft II" section and enable the "Additional command line arguments" checkbox.
A new textfield will appear where you enter "-clientapi 8080" while '8080' will be the port you are using.

Now you need to find out the your internal ip of the gaming pc. Open the commandline (cmd) on your gaming pc and type "ipconfig" and hit Enter.
In most cases the IP will look like this: 192.168.0.XX.

Go back to the Chatbot and go to the "Configuration (+Dual PC)" section and enter your IP:Port in the "Gaming PC IP:Port" field.
Example in this case: 192.168.0.XX:8080

IMPORTANT: Please do not write anything else in there or it will not work. Means no '/' or 'http://' or whatever.


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
2.0.5:
  ~ Logging is now turned off (stopped file access) when the script is disabled
  ~ Bugfix for when opponent was not found on sc2unmasked

2.0.4:
  ~ Fixes the Unbarcoding in textfiles
  ~ When playing vs. AI no check for MMR 
  ~ Avoids inactive accounts on 'Closest MMR' finding method (Threshold: 2 weeks)

2.0.3:
  ~ Included textfields in the init logging function
  ~ Minor fix with a logging function

2.0.2:
  ~ Opponent Streamer Shoutout: Added option to use Multitwitch link instead when opponent is streaming on Twitch
  ~ Added/fixed streamers from other platforms for shoutouts: Panda.tv, Azubu.tv, Douyu.tv, Afreeca
  ~ "Un-Barcoder" was renamed to "Reveal Barcodes and Smurfs"
    ~ It will also display the real name when using a smurf
    ~ Changed the way it works slightly
  ~ Overhauled the UI labels/tooltips
  ~ Added some default values for textfields/overlay textfiles
  ~ Fixes & Logging

2.0.1:
  ~ Changed methods to support Chatbot .29+ versions
  ~ Added a more detailed logging
    - Added option in "Configuration" to enable detailed logging (per default enabled)
  ~ Added a blacklist for streamer shoutouts
  ~ Fixed issue with the un-barcoding feature

2.0.0:
  ~ Renamed "Title Updater" to "MatchInfo - Twitch Title & Overlay" since more features were added then just title changing
  ~ Added the "Open readme" button
  ~ Added two buttons: First for creating the oAuth token and second for all usable variables in the fields
  ~ Overhauled the whole menu on the right
  ~ Moved the overlay files to a sub folder
  ~ Renamed the overlay files to make it more obvious/easier to distinguish
  ~ Implemented options for Region and the method to find the opponent
  - Implemented dual pc setup usage
  ~ Working together now with sc2unmasked.com / Ophilian which enables:
    - Addition of the first version of the "Un-Barcoding" feature
    - Shoutout option in chat if the opponent is streaming too
    - More accurate and more infos about opponents

1.0.2:
  ~ Necessary changes since AnkhBot became Streamlabs Chatbot
  ~ Renamed "StarCraft Accounts" to "player names"
  ~ Using regex to get MMR from RankedFTW now

1.0.1:
  ~ Added buttons that take you directly to your app creation in twitch

1.0.0:
  ~ First Release version

###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
