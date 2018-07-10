#################
Info
#################
Description: Automatic Betting System for the Game StarCraft II
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.3.3


################
Installation of the SC2 Betting System
################
To make the betting system work you only need to enable the script itself in the list of scripts and enter your Ingame StarCraft II name in one of the "Name of Account" fields in the "Player Names" section.

Now you can just jump to the "Usage of the Overlay" part if you want the overlay as well and you're ready to go or just go step-by-step through every option and read the tooltip which explains everything in detail.

___Usable Variables:
To see all the usable variables in the "Overlay Settings" and "Chat messages" click the "Overview of all Variables" button in the "Configuration Options" section. It will redirect you to the website with the list of every variable.


#################
Usage of the Overlay
#################
To enable the usage of the Overlay rightclick on the betting script and click "Insert API Key".

Afterwards click on the "Open Overlays Folder" button and drag and drop the "index.html" into your OBS.
That will create a new browser source and you just need to adjust the size of it.

___Theme: GSL
BrowserSource Size for "GSL":           Width: 850px - Height: 125px

___Theme: SC2ScoreBoard
BrowserSource Size for "SC2ScoreBoard": Width: 719px - Height: 68px

___Theme: SC2Board
BrowserSource Size for "SC2Board":      Width: 645px - Height: 316px 
You can set the FadeIn Animation in the "userSettings.js" file which is located in '..\SC2BetSystem\Overlays\'.
You got 4 options to choose from which are written there. IMPORTANT: Keep in mind that those are case-sensitive! (TopDown, BottomUp, LeftRight, RightLeft)

Note: You can just leave the size of the source at 1920x400 if you don't wont to fiddle too much with it.


For testing and setup purposes you can use the following options in the "Configuration Options" section:

___Enable the Betting vs AI. 
Now you can play a game vs AI and the script will handle it like a real bet (Betting + Chat messages + Overlay).

___Show Overlay all the time
Shows the overlay nonstop in the browsersource. That way you can adjust the overlay perfectly into your stream.

___Run a demo bet (Overlay only)
This will trigger a bet-procedure in the overlay only. That way you can test the overlay, animations and sounds.
The player infos (name + race) and the two bets are hardcoded into the script, the rest is like customized by you.


IMPORTANT: Please make sure to disable all options besides "Log Errors" if you go live. 


#################
Important Overlay Options 
#################
___Hide Bet Overlay after Closing:
After the "Time for Betting (seconds)" time has run up (which is ingame seconds) viewers can't bet/vote anymore. This option lets you decide if you want the overlay to stay during the whole game or hide afterwards and come back only to announce the winner.

___Display Percentages:
As the name says it shows the total amount bet on each side per default and with this you can switch it to a percentages based display.

___Capitalize all Names:
Uppercase for both player names. Shouldn't be used if you use barcodes for yourself unless you enjoy names like "LILILILILILI" in your overlay :D


################
Betting vs. Voting System
################
___Betting:
Per default the betting system is enabled. You set up a minimal and maximum amount to bet as well as a Win and Lose command.
That way people can use it like this: "#win (amount)"

___Voting without Currency:
If you don't want any currency you can just go to the "Voting System" section and enable "Change Betting to Voting System (w/o currency)". That way people can vote for either win or lose per command in the "Cost & Commands" section.
Example: "#win" or "#lose"

___Voting with Currency:
If you run a currency but only want people to enter "#win" or "#lose" and with a fix amount set then also enable the "Voting uses currency" checkbox. That way they also just type in the command but it uses the fix amount of your currency which you set (per default: 50).


#################
Setting up Dual PC usage
#################
Go to your "Blizzard Battle.Net Launcher" and then "Options > Game Settings". 
Scroll down until you are at the "StarCraft II" section and enable the "Additional command line arguments" checkbox.
A new textfield will appear where you enter "-clientapi 8080" while '8080' will be the port you are using.

Now you need to find out the your internal ip of the gaming pc. Open the commandline (cmd) on your gaming pc and type "ipconfig" and hit Enter.
In most cases the IP will look like this: 192.168.0.XX.

Go back to the Chatbot and go to the "Configuration Options" section and enter your IP:Port in the "Gaming PC IP:Port" field.
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
1.3.3
  ~ Added "all" command, you can now bet all the currency you have or the upper betting limit - whichever is lower
1.3.2
  ~ Added checkbox to disable all response messages
  ~ Fixed a bug when reading stored userBets.json
  ~ Added more logs in case something could not be written to a file
  ~ Disabling the script in the bot scripts overview disables the logger - removing the script is now simpler

1.3.1
  ~ Attempt on fixing some issues after the game ended
  ~ Added a more detailed logging
  ~ Adjusted the script so it works with the new streamlabs chatbot version (released 2018-02-24)

1.3.0
  ~ Added the option to use sounds for Victory/Defeat and the Start of a game
  ~ Added a button for the Error Log and Overlay folder
  ~ Fixed and implemented the proper use of dual pc setups
  ~ Fixed an important bug at the end of games which caused no winner announcement
  ~ Error logging is per default now enabled
  ~ Completely reworked the Readme.txt

1.2.3
  ~ Fixed an issue with debugging / logging

1.2.2
  ~ Added a log feature so we can backtrack problems way faster
  ~ Fixed an issue that bets would get stuck if streamer uses 'quit & rewind' feature
  ~ Fixed an issue with the 'SC2Score' theme where it got displayed before the start

1.2.1
  ~ Added the GSL theme
  ~ Hotfixes/improvements for the other themes
  ~ Added a checkbox in the overlay options to decide if you want capitalized names or not
  ~ Changed some labels, default values and tooltips
  ~ Added an 'Open readme file' button

1.2.0
  ~ Completely overhauled the sidebar menu for the script (Arrangements, labels, tooltips, etc)
  ~ Added a dropdown menu to choose from themes
  ~ Added a "SC2ScoreBoard" theme which is smaller and especially created for showing on the top border of the screen
  ~ Users can now create their own themes easily without touching existing ones
  ~ Users can also create specific variables for seperate themes (userSettings)
  ~ Added "Configure Options" for set up and test purposes
    ~ Button to do a "Test Bet": Start, Update and showing a winner
    ~ Option to be able to test it live against "AI opponents"
    ~ Option to be able to bet/vote multiple times to test alone
    ~ Option to always show the Betting overlay to adjust your OBS BrowserSource neatly
    
  ~ Fixed LOTS OF SHIT (Too lazy to write all down :D )
  ~ Reworked the core code

1.1.3
  ~ Fixed issue where both players had a name found in the list of "StarCraft II Accounts"
  ~ In case users enter wrong StarCraft Names (like with trailing white space or with character code, e.g. Burny#1337), it will now automatically correct them
  ~ Renamed "StarCraft II Accounts" to "Player Names"
  ~ Necessary changes since AnkhBot became Streamlabs Chatbot

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


###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
