"""
###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
"""

#---------------------------------------
#    Import Libraries
#---------------------------------------
import sys
import datetime
import json
import os
import time
from collections import defaultdict
from collections import OrderedDict
import threading
if __name__ != "__main__":
    import clr
import codecs
import logging


#---------------------------------------
#    [Required]    Script Information
#---------------------------------------
ScriptName = "SCII - Betting System"
Website = "http://www.brains-world.eu"
Description = "Automatic Betting System for StarCraft II"
Creator = "Brain & Burny"
Version = "1.3.3"

#---------------------------------------
#    Set Variables
#---------------------------------------
debuggingMode = True
gameUrl = "http://localhost:6119/game"
uiUrl = "http://localhost:6119/ui"
timeSinceLastUpdate = time.time()
configFile = "SC2BetSystemConfig.json"

settings = {}
responseVariables = {}
apiData = defaultdict(lambda: "")
messageQueue = []

from enum import Enum
class Status(Enum):
    open = 1
    closed = 2
    waitForMenu = 3
    waitForGame = 4

class Bets(object):
    def __init__(self):
        self.status = Status.waitForGame
        self.resetBetVariables()

    def resetBets(self):
        self.gamblers = set() # usernames of people who joined betting
        self.bets = [] #
        self.recentlyJoinedUsers = []
        self.timeSinceLastViewerJoinedBet = 0
        self.totalGambled = 0
        self.totalGambledWin = 0
        self.totalGambledLose = 0


class Settings(object):
    def __init__(self):
        self.responseInterval = 2
        self.noBetsOnlyVotes = False
        self.isPercentageBased = False
        self.capitalizeNames = True
        self.enableSounds = False

class Sc2ApiHandling(object):
    def __init__(self):
        self.apiCallDone = False
        self.latestUpdateTimestamp = time.time()
        self.timeSinceLastUpdate = time.time()
        self.duplicateNamesFound = False


# bets = {
#     "status": "waitForGame",
#     "gamblers": set(),
#     "bets": [],
#     "totalGambled": 0,
#     "apiCallDone": False,
#     "latestApiUpdateTimestamp": time.time(),
#     "totalGambledWin": 0,
#     "totalGambledLose": 0,
#     "updateRespondJoinedBetInterval": 3,
#     "updateInterval": 2,
#     "timeSinceLastViewerJoinedBet": 0,
#     "timeSinceLastUpdate": time.time(),
#     "recentlyJoinedUsers": [],
#     "noBetsOnlyVotes": False,
#     "duplicateNamesFound": False,
#     "isPercentageBased": False,
#     "capitalizeNames": True,
#     "enableSounds": False
# }

raceLongName = {
    "Z": "zerg",
    "T": "terran",
    "P": "protoss",
    "R": "random",
}

def OpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)

def BtnOpenOverlaysFolder():
    """Open the folder where the user can find the index.html"""
    location = os.path.join(os.path.dirname(__file__), "Overlays")
    os.startfile(location)

def OpenLogFolder():
    location = os.path.join(os.path.dirname(__file__), "Logs")
    os.startfile(location)

def OpenVariables():
    os.startfile("http://brains-world.eu/chatbot-starcraft-scripts-variables/")

def OpenSoundsFolder():
    location = os.path.join(os.path.dirname(__file__), "Sounds")
    os.startfile(location)

def Init():
    global responseVariables, settings, configFile, bets, gameUrl, uiUrl
    path = os.path.dirname(__file__)

    try:
        themes = [x for x in os.listdir(os.path.join(path, "Overlays")) if os.path.isdir(os.path.join(path, "Overlays", x))]
        rewriteUiConfig(dictKey="overlayThemeNames", newItems=themes, configFile=os.path.join(path, "UI_Config.json"))

        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')

        if len(settings.get("overlayThemeNames", "")) != 0:
            settings["configFileLoaded"] = True

        if settings["gamingPcIp"] != "":
            gameUrl = "http://{}/game".format(settings["gamingPcIp"])
            uiUrl = "http://{}/ui".format(settings["gamingPcIp"])
            
        if os.path.exists(os.path.join(os.path.dirname(__file__), "userBets.json")):
            with open(os.path.join(os.path.dirname(__file__), "userBets.json"), "r") as f:                
                bets["bets"] = json.load(f)
                refundBets()
                bets["bets"] = []
            try:
                with open(os.path.join(os.path.dirname(__file__), "userBets.json"), "w+") as f:
                    json.dump([], f)
            except:
                Debug("Could not clear userBets.json file. Permission error.")
    except Exception as e:
        return


    try:
        os.makedirs(os.path.join(path, "Logs"))
    except: pass
    if settings["devDebugLogging"]:        
        loggingLevel = logging.DEBUG
        # bets["logger"].debug('debug message')
        # bets["logger"].info('info message')
        # bets["logger"].warn('warn message')
        # bets["logger"].error('error message')
        # bets["logger"].critical('critical message')
    else:
        loggingLevel = logging.INFO

    try:
        bets["logger"] = logging.getLogger('SC2BetSystem')
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        logFileName = datetime.datetime.now().strftime('%Y_%m_%d.log')
        bets["filerHandler"] = logging.FileHandler(os.path.join(path, "Logs", logFileName), mode='a')
        bets["filerHandler"].setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)

        bets["logger"].setLevel(loggingLevel)
        bets["logger"].addHandler(bets["filerHandler"])
        bets["logger"].addHandler(streamHandler)  
        bets["logger"].debug("Logging started")
    except:
        Debug("Could not start logging to file. Permission error.")
    
    PushData("initThemeData")

    responseVariables = {
        "$mychannel": Parent.GetDisplayName(Parent.GetChannelName()),
        "$currencyName": Parent.GetCurrencyName(),
        "$cmdBetWin": settings["cmdBetWin"],
        "$cmdBetLose": settings["cmdBetLose"],
        "$cmdAbort": settings["cmdAbort"],
        "$rewardMultiplier": settings["rewardMultiplier"],
        "$minBet": settings["minBet"],
        "$maxBet": settings["maxBet"],
        "$fixedAmount": settings["fixedVotingAmount"],
    }
    
    settings["streamerUsernames"] = []
    settings["streamerUsernames"].append(settings["bnetUsername1"].lower().strip())
    settings["streamerUsernames"].append(settings["bnetUsername2"].lower().strip())
    settings["streamerUsernames"].append(settings["bnetUsername3"].lower().strip())
    settings["streamerUsernames"].append(settings["bnetUsername4"].lower().strip())
    settings["streamerUsernames"].append(settings["bnetUsername5"].lower().strip())
    bets["updateRespondJoinedBetInterval"] = int(settings["betUserCollectionTime"])

    responseVariables["$totalAmountGambled"] = 0
    responseVariables["$totalPointsWon"] = "0"
    responseVariables["$totalPointsLost"] = "0"
    responseVariables["$winnersNames"] = ""
    responseVariables["$winnersWithAmount"] = ""
    responseVariables["$losersNames"] = ""
    responseVariables["$losersWithAmount"] = ""
    responseVariables["$betDuration"] = str(int(settings["betDuration"]))
    responseVariables["$rewardMultiplier"] = str(settings["rewardMultiplier"])
    try:
        responseVariables["$minBet"] = str(int(settings["minBet"]))
    except ValueError:
        settings["minBet"] = 0
        responseVariables["$minBet"] = "0"
    try:
        responseVariables["$maxBet"] = str(int(settings["maxBet"]))
    except ValueError:
        settings["maxBet"] = 9999999999999
        responseVariables["$maxBet"] = "9999999999999"
    settings["betChoices"] = [settings["cmdBetWin"].lower(), settings["cmdBetLose"].lower()]
    return

def ReloadSettings(jsonData):
    Init()
    return

def ScriptToggled(state):
    global bets
    if not state:
        # unload logger so files can be removed
        bets["logger"].setLevel(logging.WARNING)
        bets["logger"].removeHandler(bets["filerHandler"])
        bets["filerHandler"].close()


#---------------------------------------
# Communication with the Overlay
#---------------------------------------
def PushData(eventName):
    global responseVariables, bets, settings

    if eventName == "start":
        Parent.BroadcastWsEvent("EVENT_INIT_THEME", json.dumps({"themeName": settings["overlayThemeNames"]}, ensure_ascii=False))

        tempChatCmdWin = settings["overlayChatCmdWin"]
        tempChatCmdLose = settings["overlayChatCmdLose"]
        tempLblWin = settings["overlayLabelWin"]
        tempLblLose = settings["overlayLabelLose"]

        for variable, text in responseVariables.items():
            tempChatCmdWin = tempChatCmdWin.replace(variable, str(text))
            tempChatCmdLose = tempChatCmdLose.replace(variable, str(text))
            tempLblWin = tempLblWin.replace(variable, str(text))
            tempLblLose = tempLblLose.replace(variable, str(text))

        overlayDictionary = {
            "durationShowWinner": settings["overlayShowWinnerDuration"] * 1000,
            "hideAfterBetClosed": settings["overlayHideBetAfterClosed"],
            "title": settings["overlayTitle"],
            "chatCmdWin": tempChatCmdWin[:20],
            "chatCmdLose": tempChatCmdLose[:20],
            "lblWin": tempLblWin[:24],
            "lblLose": tempLblLose[:24],
            "player1": responseVariables["$player1"][:15],
            "player2": responseVariables["$player2"][:15],
            "race1": raceLongName[responseVariables["$race1"]],
            "race2": raceLongName[responseVariables["$race2"]],
            "totalWin": str(int(bets["totalGambledWin"])),
            "totalLose": str(int(bets["totalGambledLose"])),
            "lblCurr": settings["overlayCurrencyShortName"][:8],
            "isPercentageBased": bets["isPercentageBased"],
            "themeName": settings["overlayThemeNames"],
            "showOverlay": settings["devShowOverlay"],
            "enabledSounds": settings["enableSounds"],
            "soundStart": settings["soundStart"],
            "soundVictory": settings["soundVictory"],
            "soundDefeat": settings["soundDefeat"],
            "volumeStart": settings["soundStartVolume"],
            "volumeVictory": settings["soundVictoryVolume"],
            "volumeDefeat": settings["soundDefeatVolume"]
        }
        if bets["isPercentageBased"]: #set both percentages to 50% at the start of a new bet, instead of both 0%
            overlayDictionary["totalWin"] = "50"
            overlayDictionary["totalLose"] = "50"
            overlayDictionary["lblCurr"] = "%"
            overlayDictionary["isPercentageBased"] = bets["isPercentageBased"]
        if overlayDictionary["lblCurr"] == "":
            overlayDictionary["lblCurr"] = Parent.GetCurrencyName()

        Parent.BroadcastWsEvent("EVENT_BET_START", json.dumps(overlayDictionary, ensure_ascii=False))

    elif eventName == "end":
        Parent.BroadcastWsEvent("EVENT_BET_END", None)
    elif eventName == "update":
        if bets["isPercentageBased"]:
            totalTemp = max(1, int(bets["totalGambledWin"]) + int(bets["totalGambledLose"]))
            overlayDictionary = {
                "totalWin": round(100 * int(bets["totalGambledWin"]) / totalTemp),
                "totalLose": 100 - round(100 * int(bets["totalGambledWin"]) / totalTemp),
                "lblCurr": "%",
            }
        else:
            overlayDictionary = {
                "totalWin": int(bets["totalGambledWin"]),
                "totalLose": int(bets["totalGambledLose"]),
                "lblCurr": settings["overlayCurrencyShortName"][:8],
            }
        overlayDictionary["isPercentageBased"] = bets["isPercentageBased"]
        if overlayDictionary["lblCurr"] == "":
            overlayDictionary["lblCurr"] = Parent.GetCurrencyName()[:8]
        Parent.BroadcastWsEvent("EVENT_BET_UPDATE", json.dumps(overlayDictionary, ensure_ascii=False))

    elif eventName == "abort":
        Parent.BroadcastWsEvent("EVENT_BET_ABORT", None)

    elif eventName == "win":
        Parent.BroadcastWsEvent("EVENT_BET_WIN", None)

    elif eventName == "lose":
        Parent.BroadcastWsEvent("EVENT_BET_LOSE", None)

    elif eventName == "initThemeData":
        Parent.BroadcastWsEvent("EVENT_INIT_THEME", json.dumps({
            "themeName": settings["overlayThemeNames"]            
            }, ensure_ascii=False))
        if settings["devShowOverlay"]:
            Parent.BroadcastWsEvent("EVENT_BET_SHOW", None)
    return

def Execute(data):
    global settings, bets, responseVariables
    
    if settings.get("configFileLoaded", False):
        if data.IsChatMessage():
            responseVariables["$user"] = data.UserName
            responseVariables["$points"] = str(Parent.GetPoints(data.User))

            if data.GetParamCount() == 1 and data.GetParam(0).lower() == settings["cmdAbort"]:
                if bets["status"] in ["open", "closed"] \
                    and ((settings["allowModsToAbort"] and Parent.HasPermission(data.User, "Moderator", "")) \
                    or Parent.HasPermission(data.User, "Caster", "")):

                    refundBets()

                    bets["bets"] = []
                    bets["status"] = "waitForMenu"
                    PushData("abort")
                    SendMessage(settings["responseBetCanceled"])

            elif data.GetParamCount() >= 1 and data.GetParam(0).lower() in settings["betChoices"] and bets["status"] == "open":
                try:
                    #this part is about the betting system, e.g. "#win 50"
                    if not bets["noBetsOnlyVotes"]:
                        if data.GetParamCount() >= 2:
                            # TODO: might replace "all" with a customizable textfield in the future
                            if data.GetParam(1).lower() == "all":
                                availableAmount = min(int(settings["maxBet"]), Parent.GetPoints(data.User))
                                addGambler(data.User, data.UserName, availableAmount, data.GetParam(0))
                            else:
                                addGambler(data.User, data.UserName, int(data.GetParam(1)), data.GetParam(0))
                            PushData("update")
                        else:
                            SendMessage(settings["responseHowToUseBetCommand"])

                    else: #this part is about the voting system (when betting was changed to voting), e.g. "#win"
                        if data.User in bets["gamblers"] and not settings["devAllowMultipleEntries"]:
                            SendMessage(settings["responseUserAlreadyPlacedBet"])
                        else:
                            if bets["votingUsesCurrency"]:
                                if Parent.GetPoints(data.User) >= bets["fixedVotingAmount"]:
                                    addGambler(data.User, data.UserName, bets["fixedVotingAmount"], data.GetParam(0), ignoreCheck=True)
                                    PushData("update")
                                else:
                                    SendMessage(settings["responseNotEnoughPoints"])
                            else:                                
                                addGambler(data.User, data.UserName, 0, data.GetParam(0), ignoreCheck=True)
                                PushData("update")
                except ValueError:
                    SendMessage(settings["responseHowToUseBetCommand"])
    return

def Tick():
    global apiData, settings, bets, responseVariables, messageQueue

    if settings.get("configFileLoaded", False):
        time1 = time.time()

        for item in messageQueue:
            if item["deliverTime"] < time1:
                SendMessage(item["message"])
                messageQueue.remove(item)
                break

        if time1 - bets["timeSinceLastViewerJoinedBet"] > bets["updateRespondJoinedBetInterval"] and len(bets["recentlyJoinedUsers"]) > 0:
            bets["timeSinceLastViewerJoinedBet"] = time1
            SendMessage(settings["responseUserJoinedBet"])
            bets["recentlyJoinedUsers"] = []

        if time1 - bets["timeSinceLastUpdate"] > bets["updateInterval"]:
            bets["timeSinceLastUpdate"] = time1
            if bets["apiCallDone"]:
                bets["apiCallDone"] = False
                # - "waitForGame" means the script waits for a new game to launch so it can open a new bet
                # - "open" means the betting is open and viewers are able to bet/vote
                # - "closed" means the game has gone past bets["betDuration"] and viewers can no longer gamble
                # - "abort" means "!abort" command was used or the game has ended before bets["betDuration"] has passed
                # - "waitForMenu" can have several reasons that make the script wait to until the streamer is back in sc2 menu
                
                if bets["status"] in ["waitForGame"]:
                    if apiData["inStarcraftLocation"] == "1v1Replay":
                        # fix by hups: if streamers goes into replay, script will deactivate until streamer is back in menu (disable betting at resume from replay)
                        bets["logger"].debug("Streamer went into replay - script disabled until streamer goes back into sc2 menu.")
                        bets["status"] = "waitForMenu"
                    elif bets["duplicateNamesFound"] and apiData["inStarcraftLocation"] in ["1v1AsPlayer"]:
                        # if duplicate names have been found, instantly close the bet system - no overlay will show up
                        bets["logger"].debug("----------------------------")
                        bets["logger"].debug("New game has started. Both names (streamer and opponent) are listed in the \"Player Names\" of the streamer. Names are {} ({}) and {} ({})".format(apiData["player1Name"], apiData["player1Race"], apiData["player2Name"], apiData["player2Race"]))
                        SendMessage(settings["responseTwoMatchingNames"])
                        bets["status"] = "waitForMenu"

                    elif apiData["inStarcraftLocation"] in ["1v1AsPlayer"] and int(apiData["ingameSecs"]) < int(settings["betDuration"]):
                        bets["logger"].debug("----------------------------")
                        bets["logger"].debug("New game: {} ({}) vs {} ({})".format(apiData["player1Name"], apiData["player1Race"], apiData["player2Name"], apiData["player2Race"]))
                        resetBetVariables()
                        SendMessage(settings["responseBetOpened"])
                        PushData("start")
                    else:
                        # script gets here if streamer is in menu / replay / starcraft not running
                        pass

                elif bets["status"] in ["waitForMenu"]:
                    if apiData["inStarcraftLocation"] == "menu":
                        bets["status"] = "waitForGame"
                        bets["logger"].debug("Streamer is now in menu.")
                    else:
                        # script gets here if streamer is in game but the bet was canceled (duplicate name, or #abort command)
                        pass

                elif bets["status"] in ["open"]:                    
                    if int(apiData["ingameSecs"]) > int(settings["betDuration"]) and bets["status"] == "open":
                        # closing the bet because the in-game time passed the betDuration
                        bets["logger"].debug("--- Bet closed ---")
                        bets["status"] = "closed"
                        PushData("end")
                        try:
                            with open(os.path.join(os.path.dirname(__file__), "userBets.json"), "w+") as f:
                                json.dump(bets["bets"], f, indent=4)
                        except:
                            Debug("Could not clear userBets.json file. Permission error.")
                        SendMessage(settings["responseBetClosed"])

                    elif apiData["player1Result"] != "undecided":
                        # cancels the bets
                        bets["logger"].debug("Game ended before the bets closed. Gamblers are being refunded.")
                        refundBets()
                        bets["bets"] = []
                        bets["status"] = "waitForGame"
                        PushData("abort")
                        SendMessage(settings["responseBetCanceled"])
                    else:
                        # gets here every tick when the game is running (before bet["duration"] - do nothing
                        pass

                elif bets["status"] in ["closed"]:    
                    if apiData["player1Result"] != "undecided":
                        # paying out the correct bets
                        bets["logger"].debug("Game ended after the bets closed. Gamblers are being paid out.")

                        # set local variables
                        totalPointsWon = 0
                        totalPointsLost = 0
                        userListCorrectGamble = []
                        userListCorrectGambleWithAmount = []
                        userListWrongGamble = []
                        userListWrongGambleWithAmount = []

                        betWinnerCommand = ""
                        if apiData["player1Result"] == "victory":
                            betWinnerCommand = bets["cmdBetWin"].lower()
                            bets["logger"].debug("Game end: Streamer won against {} ({}), sending EVENT_BET_WIN".format(apiData["player2Name"], apiData["player2Race"]))
                            PushData("win")
                        elif apiData["player1Result"] == "defeat":
                            betWinnerCommand = bets["cmdBetLose"].lower()
                            bets["logger"].debug("Game end: Streamer lost against {} ({}), sending EVENT_BET_LOSE".format(apiData["player2Name"], apiData["player2Race"]))
                            PushData("lose")

                        # paying out viewers/betters who placed a bet or a vote (only if the vote-with-currency was on)

                        # calculate the total correct/wrong bets and the amount the users won                            
                        userPointsWon = [{"userid": bet["userid"], "username": bet["username"], "betInvestment": int(round(bets["rewardMultiplier"] * bet["betInvestment"]))} for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand]
                        for betEntry in userPointsWon:
                            bets["logger"].debug("Payout - Gambled correct: {} - {}".format(betEntry["username"], betEntry["betInvestment"]))
                            Parent.AddPoints(betEntry["userid"], betEntry["username"], betEntry["betInvestment"])

                        # just for logging: users who lost their points
                        userPointsLost = {bet["username"]: bet["betInvestment"] for bet in bets["bets"] if bet["betChoice"] != betWinnerCommand}
                        for wrongGambler, amountLost in userPointsLost.items():
                            bets["logger"].debug("Payout - Gambled wrong: {} - {}".format(wrongGambler, amountLost))

                        totalPointsWon = sum([userPointsWon[bet["username"]] for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand])
                        totalPointsLost = sum([bet["betInvestment"] for bet in bets["bets"] if bet["betChoice"] != betWinnerCommand])
                        
                        userListCorrectGamble = ["@" + bet["username"] for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand]
                        userListCorrectGambleWithAmount = ["@{} ({})".format(bet["username"], userPointsWon[bet["username"]]) for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand]
                        
                        userListWrongGamble = ["@" + bet["username"] for bet in bets["bets"] if bet["betChoice"] != betWinnerCommand]
                        userListWrongGambleWithAmount = ["@{} ({})".format(bet["username"], bet["betInvestment"]) for bet in bets["bets"] if bet["betChoice"] != betWinnerCommand]

                        bets["bets"] = []
                        responseVariables["$totalPointsWon"] = totalPointsWon
                        responseVariables["$totalPointsLost"] = totalPointsLost
                        responseVariables["$winnersNames"] = ", ".join(userListCorrectGamble)
                        responseVariables["$winnersWithAmount"] = ", ".join(userListCorrectGambleWithAmount)
                        responseVariables["$losersNames"] = ", ".join(userListWrongGamble)
                        responseVariables["$losersWithAmount"] = ", ".join(userListWrongGambleWithAmount)
                        messageDelay = settings["betWinnerAnnoucementDelay"]
                        if apiData["player1Result"] == "victory":
                            if bets["totalGambled"] == 0:
                                SendMessage(settings["responseVictoryNoBets"], delayInSeconds=messageDelay)
                            elif totalPointsWon == 0:
                                SendMessage(settings["responseVictoryWrongBets"], delayInSeconds=messageDelay)
                            else:
                                SendMessage(settings["responseVictoryCorrectBets"], delayInSeconds=messageDelay)
                        elif apiData["player1Result"] == "defeat":
                            if bets["totalGambled"] == 0:
                                SendMessage(settings["responseDefeatNoBets"], delayInSeconds=messageDelay)
                            elif totalPointsWon == 0:
                                SendMessage(settings["responseDefeatWrongBets"], delayInSeconds=messageDelay)
                            else:
                                SendMessage(settings["responseDefeatCorrectBets"], delayInSeconds=messageDelay)
                        bets["status"] = "waitForMenu"
                        try:
                            with open(os.path.join(os.path.dirname(__file__), "userBets.json"), "w+") as f:
                                json.dump([], f)
                        except:
                            Debug("Could not clear userBets.json file. Permission error.")

                    else:
                        # script goes here if streamer is in a game past bets["betDuration"] - so the script is basically waiting for the game to finish and streamer going back into menu - do nothing
                        pass            

            else:
                threading.Thread(target=GetSc2ApiResponse, args=()).start()
    return

##################
# HELPER FUNCTIONS
##################

# sends message to streamer's twitch channel with variables replaced by text
def SendMessage(string, delayInSeconds=0):
    global responseVariables, messageQueue, settings
    if settings["cbEnableResponses"]:
        for variable, text in responseVariables.items():
            if type(text) == type(0.1):
                string = string.replace(variable, str(int(text)))
            else:
                string = string.replace(variable, str(text))
        if delayInSeconds == 0:
            Parent.SendStreamMessage(string[:490])
        else:
            messageQueue.append({
                "deliverTime": int(time.time()) + delayInSeconds,
                "message": string
            })

def GetSc2ApiResponse():
    global gameUrl, uiUrl, bets, settings
    try:
        gameResponse = json.loads(json.loads(Parent.GetRequest(gameUrl, {}))['response'])
        uiResponse = json.loads(json.loads(Parent.GetRequest(uiUrl, {}))['response'])
        time1 = time.time()
        if bets["latestApiUpdateTimestamp"] < time1:
            bets["latestApiUpdateTimestamp"] = time1
            if ProcessClientApiData(gameResponse, uiResponse):
                return True

    except Exception as e:
        if bets["status"] in ["open", "closed"]:
            bets["status"] = "waitForGame"
            refundBets()
            bets["bets"] = []
            SendMessage(settings["responseStarcraftClosed"])
    return False

def ProcessClientApiData(gameResponse, uiResponse):
    global apiData, bets, settings
    try:
        if len(gameResponse["players"]) == 2:
            apiData["player1Race"] = gameResponse["players"][0]["race"][0].upper()
            apiData["player2Race"] = gameResponse["players"][1]["race"][0].upper()
            apiData["player1Name"] = gameResponse["players"][0]["name"]
            apiData["player2Name"] = gameResponse["players"][1]["name"]
            apiData["player1Result"] = gameResponse["players"][0]["result"].lower()
            apiData["player2Result"] = gameResponse["players"][1]["result"].lower()
            apiData["ingameMins"] = str(int(gameResponse["displayTime"])//60)
            apiData["ingameSecs"] = str(int(gameResponse["displayTime"]))

            if apiData["player1Name"].lower() in settings["streamerUsernames"]:
                apiData["streamerIsInValid1v1Game"] = True
                if gameResponse["players"][1]["type"] == "computer":
                    if not settings["devEnableVsAi"]:
                        apiData["streamerIsInValid1v1Game"] = False
            elif apiData["player2Name"].lower() in settings["streamerUsernames"]:
                apiData["player1Race"], apiData["player2Race"] = apiData["player2Race"], apiData["player1Race"]
                apiData["player1Name"], apiData["player2Name"] = apiData["player2Name"], apiData["player1Name"]
                apiData["player1Result"], apiData["player2Result"] = apiData["player2Result"], apiData["player1Result"]
                apiData["streamerIsInValid1v1Game"] = True
                if gameResponse["players"][0]["type"] == "computer":
                    if not settings["devEnableVsAi"]:
                        apiData["streamerIsInValid1v1Game"] = False
            else:
                apiData["streamerIsInValid1v1Game"] = False
            # both names (streamer and his opponent) have a username that is in the list of usernames of the streamer (e.g. this can be the case when both have the same barcodes)
            if apiData["player1Name"].lower() in settings["streamerUsernames"] and apiData["player2Name"].lower() in settings["streamerUsernames"] :
                apiData["streamerIsInValid1v1Game"] = False
                bets["duplicateNamesFound"] = True
            else:
                bets["duplicateNamesFound"] = False
            matchup = apiData["player1Race"] + "v" + apiData["player2Race"]

            if apiData["streamerIsInValid1v1Game"]:
                responseVariables["$player1"] = apiData["player1Name"]
                responseVariables["$player2"] = apiData["player2Name"]
                responseVariables["$race1"] = apiData["player1Race"]
                responseVariables["$race2"] = apiData["player2Race"]

            # only change the location variable if duplicate names haven't been found
            # if not bets["duplicateNamesFound"]:
            if uiResponse["activeScreens"] == []:
                if len(gameResponse["players"]) == 2:
                    if gameResponse["isReplay"]:
                        apiData["inStarcraftLocation"] = "1v1Replay"
                    else:
                        if apiData["streamerIsInValid1v1Game"]:
                            apiData["inStarcraftLocation"] = "1v1AsPlayer"
                        else:
                            apiData["inStarcraftLocation"] = "1v1AsCaster"
                else:
                    apiData["inStarcraftLocation"] = "other"
            else:
                apiData["inStarcraftLocation"] = "menu"
            bets["apiCallDone"] = True
            return True

    except Exception as e:
        if bets["status"] in ["open", "closed"]:
            bets["status"] = "waitForGame"
            refundBets()
            bets["bets"] = []
            SendMessage(settings["responseStarcraftClosed"])
        print("Unknown error while attempting to collect data from SC2 API:", e)
    return False

##################
# betting related
##################

def resetBetVariables():
    global bets, responseVariables, settings
    bets["status"] = "open"
    bets["bets"] = []
    bets["gamblers"] = set()
    bets["recentlyJoinedUsers"] = []
    bets["totalGambled"] = 0
    bets["totalGambledWin"] = 0
    bets["totalGambledLose"] = 0
    responseVariables["$totalAmountGambled"] = 0
    responseVariables["$totalPointsWon"] = "0"
    responseVariables["$totalPointsLost"] = "0"
    responseVariables["$winnersNames"] = ""
    responseVariables["$winnersWithAmount"] = ""
    responseVariables["$losersNames"] = ""
    responseVariables["$losersWithAmount"] = ""
    # settings all these following variables to local variables in case the streamer changes the variables while a game is running
    bets["noBetsOnlyVotes"] = settings["noBetsOnlyVotes"]
    bets["isPercentageBased"] = settings["isPercentageBased"]
    bets["votingUsesCurrency"] = settings["votingUsesCurrency"]
    bets["fixedVotingAmount"] = settings["fixedVotingAmount"]
    bets["cmdBetWin"] = settings["cmdBetWin"]
    bets["cmdBetLose"] = settings["cmdBetLose"]
    bets["rewardMultiplier"] = settings["rewardMultiplier"]

def payoutCorrectBets():
    pass

def gamblerAllowedToJoin(userid, investmentAmount):
    global bets
    if Parent.GetPoints(userid) < investmentAmount:
        SendMessage(settings["responseNotEnoughPoints"])
        return False
    if userid in bets["gamblers"] and not settings["devAllowMultipleEntries"]:
        SendMessage(settings["responseUserAlreadyPlacedBet"])
        return False
    if investmentAmount < int(settings["minBet"]) or investmentAmount > int(settings["maxBet"]):
        SendMessage(settings["responseNotCorrectBetAmount"])
        return False
    return True

def addGambler(userid, username, investmentAmount, betChoice, ignoreCheck=False):
    global bets, settings, responseVariables
    if ignoreCheck or gamblerAllowedToJoin(userid, investmentAmount):
        bets["bets"].append({"userid": userid, "username": username, "betChoice": betChoice.lower(), "betInvestment": investmentAmount})
        Parent.RemovePoints(userid, username, investmentAmount)
        bets["gamblers"].add(userid)
        bets["recentlyJoinedUsers"].append("@" + username)
        responseVariables["$recentlyJoinedUsers"] = ", ".join(bets["recentlyJoinedUsers"])
        bets["timeSinceLastViewerJoinedBet"] = time.time()
        bets["totalGambled"] += investmentAmount
        responseVariables["$totalAmountGambled"] = str(bets["totalGambled"])
        if betChoice.lower() == bets["cmdBetWin"].lower():
            bets["totalGambledWin"] += investmentAmount
        else:
            bets["totalGambledLose"] += investmentAmount
        bets["logger"].debug("Bet join: {} - {} - {}".format(username, investmentAmount, betChoice))

def refundBets():
    global bets
    if len(bets["bets"]) > 0:
        bets["logger"].debug("Refunding {} bets".format(len(bets["bets"])))
    for bet in bets["bets"]: # paying back viewers who already placed a bet if the game ended before "betDuration" ran out or when the abort command was used
        bets["logger"].debug("Refund: {} ({})".format(bet["username"], bet["betInvestment"]))
        Parent.AddPoints(bet["userid"], bet["username"], bet["betInvestment"])
    pass

# writes new themes to the UI_Config.json
def rewriteUiConfig(dictKey, newItems, configFile=""):
    dictionary = OrderedDict()
    oldItems = []
    with codecs.open(configFile, encoding='utf-8-sig', mode='r') as file:
        dictionary = json.load(file, encoding='utf-8-sig', object_pairs_hook=OrderedDict)
        oldItems = dictionary[dictKey]["items"]
        dictionary[dictKey]["items"] = newItems
        if len(dictionary[dictKey]["items"]) > 0:
            dictionary[dictKey]["value"] = dictionary[dictKey]["value"] if dictionary[dictKey]["value"] in dictionary[dictKey]["items"] else dictionary[dictKey]["items"][0]
    
    if dictionary != OrderedDict() and sorted(oldItems) != sorted(newItems):
        try:
            with codecs.open(configFile, encoding='utf-8-sig', mode='w') as file:
                json.dump(dictionary, file, encoding='utf-8-sig', indent=4, sort_keys=False)
        except:
            Debug("Could refresh list of available overlays. Permission error.")
            # Debug("Successfully rewritten ui config file")

def TestOverlay():
    global bets, settings, responseVariables
    if settings.get("configFileLoaded", False):
        if not bets.get("TestOverlayActive", False):
            bets["TestOverlayActive"] = True
            threading.Thread(target=TestOverlayThread, args=()).start()

def TestOverlayThread():
    global bets, settings, responseVariables

    sleepTime = 5

    Parent.BroadcastWsEvent("EVENT_INIT_THEME", json.dumps({"themeName": settings["overlayThemeNames"]}, ensure_ascii=False))

    tempChatCmdWin = settings["overlayChatCmdWin"]
    tempChatCmdLose = settings["overlayChatCmdLose"]
    tempLblWin = settings["overlayLabelWin"]
    tempLblLose = settings["overlayLabelLose"]

    for variable, text in responseVariables.items():
        tempChatCmdWin = tempChatCmdWin.replace(variable, str(text))
        tempChatCmdLose = tempChatCmdLose.replace(variable, str(text))
        tempLblWin = tempLblWin.replace(variable, str(text))
        tempLblLose = tempLblLose.replace(variable, str(text))

    overlayDictionary = {
        "durationShowWinner": settings["overlayShowWinnerDuration"] * 1000,
        "hideAfterBetClosed": settings["overlayHideBetAfterClosed"],
        "title": settings["overlayTitle"],
        "chatCmdWin": tempChatCmdWin[:20],
        "chatCmdLose": tempChatCmdLose[:20],
        "lblWin": tempLblWin[:24],
        "lblLose": tempLblLose[:24],
        "player1": "BrainLongNameeeee"[:15],
        "player2": "Burny"[:15],
        "race1": "zerg",
        "race2": "terran",
        "totalWin": "0",
        "totalLose": "0",
        "lblCurr": settings["overlayCurrencyShortName"][:8],
        "isPercentageBased": settings["isPercentageBased"],
        "themeName": settings["overlayThemeNames"],
        "showOverlay": settings["devShowOverlay"],
        "capitalizeNames": settings["capitalizeNames"],
        "enabledSounds": settings["enableSounds"],
        "soundStart": settings["soundStart"],
        "soundVictory": settings["soundVictory"],
        "soundDefeat": settings["soundDefeat"],
        "volumeStart": settings["soundStartVolume"],
        "volumeVictory": settings["soundVictoryVolume"],
        "volumeDefeat": settings["soundDefeatVolume"]
    }
    if settings["isPercentageBased"]:
        overlayDictionary["totalWin"] = "50"
        overlayDictionary["totalLose"] = "50"
        overlayDictionary["lblCurr"] = "%"
        overlayDictionary["isPercentageBased"] = settings["isPercentageBased"]
    if overlayDictionary["lblCurr"] == "":
        overlayDictionary["lblCurr"] = Parent.GetCurrencyName()

    Parent.BroadcastWsEvent("EVENT_BET_START", json.dumps(overlayDictionary, ensure_ascii=False))


    time.sleep(11)
    # UPDATE - LOSE 
    if settings["isPercentageBased"]:
        overlayDictionary = {
            "totalWin": 0,
            "totalLose": 100,
            "lblCurr": "%",
        }
    else:
        overlayDictionary = {
            "totalWin": 0,
            "totalLose": 69,
            "lblCurr": settings["overlayCurrencyShortName"][:8],
        }
    overlayDictionary["isPercentageBased"] = settings["isPercentageBased"]
    if overlayDictionary["lblCurr"] == "":
        overlayDictionary["lblCurr"] = Parent.GetCurrencyName()[:8]
    Parent.BroadcastWsEvent("EVENT_BET_UPDATE", json.dumps(overlayDictionary, ensure_ascii=False))


    time.sleep(sleepTime)
    # UPDATE - WIN 

    if settings["isPercentageBased"]:
        overlayDictionary.update({
            "totalWin": 69,
            "totalLose": 31
        })
    else:
        overlayDictionary.update({
            "totalWin": 420
        })
    Parent.BroadcastWsEvent("EVENT_BET_UPDATE", json.dumps(overlayDictionary, ensure_ascii=False))
    
    time.sleep(sleepTime)
    # Bet Closed (Hide Bet if option enabled)
    Parent.BroadcastWsEvent("EVENT_BET_END", None)

    time.sleep(sleepTime)
    # WINNER SHOWN
    Parent.BroadcastWsEvent("EVENT_BET_WIN", None)
    # BET OVER

    bets["TestOverlayActive"] = False

def Debug(message):
    if debuggingMode:
        Parent.Log("Betting", message)


#---------------------------------------
#    For standalone betting and debugging
#---------------------------------------

# Same as StreamlabsChatbot
class Parent(object):
    def GetDisplayName(self, dataUser):
        pass
    def GetChannelName(self):
        pass
    def GetCurrencyName(self):
        pass
    def BroadcastWsEvent(self):
        pass
    def GetPoints(self, dataUser):
        pass
    def AddPoints(self, dataUser):
        pass
    def RemovePoints(self, dataUser):
        pass
    def Log(self, scriptName, message):
        pass
    def SendStreamMessage(self, message): # 490 or 500 character limit
        pass
    def GetRequest(self, url, data: dict):
        pass

# Same as StreamlabsChatbot
class Data(object):
    def IsChatMessage(self):
        pass
    def UserName(self):
        pass
    def User(self):
        pass
    def GetParamCount(self):
        pass
    def GetParam(self, index):
        pass

# Emulate a User
class User(object):
    def __init__(self, userName, user, points):
        self.userName = userName
        self.user = user
        self.points = points

# Twitch IRC connection
import socket
import re
import json




class Bot(object):
    """"""
    def __init__(self, channel, n_msg_per_sec=100):
        super(Bot, self).__init__()
        self._nickname = NICK
        self.channel = channel
        self.connect(channel)
        # print(NICK, channel, '\n', '-' * (len(NICK + channel) + 1))
        print("{} {}\n{}".format(NICK, channel, '-' * (len(NICK + channel) + 1)))

        self._msg_count = 0
        self.n_msg_per_sec = n_msg_per_sec

    def connect(self, channel):
        self._socket = socket.socket()
        self._socket.connect((HOST, PORT))
        self._socket.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        self._socket.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        self._socket.send("JOIN {}\r\n".format(channel).encode("utf-8"))

    def chat(self, msg):
        self._socket.send("PRIVMSG {} :{}\r\n".format(self.channel, msg))

    def _ping_pong(self, response):
        if response == "PING :tmi.twitch.tv\r\n":
            # send pong back to prevent timeout
            self._socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            return True
        else:
            return False

    def _get_response(self):
        try:
            response = self._socket.recv(1024).decode("utf-8")
        except UnicodeDecodeError as e:
            print('\n\n%s\n\n' % e)
            return False

        if self._ping_pong(response):
            return False
        elif ':tmi.twitch.tv' in response:
            return False
        else:
            return response

    def _process_msg(self, response):
        username = re.search(r"\w+", response).group(0)
        mask = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
        message = mask.sub("", response).strip('\r\n')
        return username, message

    def action(self, username, msg):
        return NotImplementedError()

    def run(self):
        while True:
            response = self._get_response()
            if response:
                username, msg = self._process_msg(response)
                self.action(username, msg)

            time.sleep(1 / float(self.n_msg_per_sec))



if __name__ == "__main__":
    # Initialize bot
    import json, os


    # Load normal config files and values set by StreamlabsChatbot
    if os.path.exists("SC2BetSystemConfig.json"):
        with open("SC2BetSystemConfig.json") as f:
            settings = json.load(f)
    else:
        # TODO: parse ui_config json and default values
        with open("UI_Config.json") as f:
            settings = json.load(f)

    # Load or create standalone config
    if os.path.exists("SC2BetStandaloneConfig.json"):
        with open("SC2BetStandaloneConfig.json") as f:
            standaloneSettings = json.load(f)
    else:
        with open("SC2BetStandaloneConfig.json", "w") as f:
            defaultJson = OrderedDict()
            defaultJson["name"] = ""
            defaultJson["pass"] = ""
            defaultJson["channel"] = ""
            json.dump(defaultJson, f, indent=4)
        _ = input(
"""
Standalone-config file was not found and has been created.
Please put in your bot name, password or oauth and which channel to join.
""")

    HOST = config['HOST']
    PORT = config['PORT']
    NICK = config['NICK']
    PASS = config['PASS']
    """
    HOST = "irc.twitch.tv"                          # Hostname of the IRC-Server in this case twitch's
    PORT = 6667                                     # Default IRC-Port
    CHAN = "#testing"                               # Channelname = #{Nickname}
    NICK = "Testing"                                # Nickname = Twitch username
    PASS = "oauth:asdfg12345asdfg12345asdfg12345"   # www.twitchapps.com/tmi/ will help to retrieve the required authkey
    """


    # Run bot while-loop

    pass

