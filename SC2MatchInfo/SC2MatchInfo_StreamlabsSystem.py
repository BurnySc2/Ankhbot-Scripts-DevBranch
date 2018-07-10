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
import time
import os
from collections import defaultdict
import threading
import clr
import codecs
import logging

#---------------------------------------
#    [Required]    Script Information
#---------------------------------------
ScriptName = "SCII - MatchInfo"
Website = "http://www.brains-world.eu"
Description = "Live info from matches for Twitch Title & custom text files for StarCraft II"
Creator = "Brain & Burny"
Version = "2.0.5"

#---------------------------------------
#    Set Variables
#---------------------------------------
debuggingMode = True
configFile = "SC2MatchInfoConfig.json"

matchInfo = {
    "channel": "",
    "clientId": "",
    "oauth": "",
    "inGameIds": [],

    "titleInGameAsPlayer": "",
    "titleInGameAsCaster": "",
    "titleInGameAsOther": "",
    "titleInMenu": "",
    "titleIn1v1Replay": "",

    "overlayText1": "",
    "overlayText2": "",
    "overlayText3": "",
    "overlayText4": "",
    "overlayText5": "",
    "overlayText6": "",

    "overlayText41": "",
    "overlayText42": "",
    "overlayText43": "",

    "overlayText51": "",
    "overlayText52": "",
    "overlayText53": "",

    "overlayText61": "",
    "overlayText62": "",
    "overlayText63": "",

    "overlayText1Written": "",
    "overlayText2Written": "",
    "overlayText3Written": "",

    "overlayText4Written": "",
    "overlayText5Written": "",
    "overlayText6Written": "",

    "overlayText1path": "Overlay\MatchInfo - On Change 1.txt",
    "overlayText2path": "Overlay\MatchInfo - On Change 2.txt",
    "overlayText3path": "Overlay\MatchInfo - On Change 3.txt",
    "overlayText4path": "Overlay\MatchInfo - Change On Scene 1.txt",
    "overlayText5path": "Overlay\MatchInfo - Change On Scene 2.txt",
    "overlayText6path": "Overlay\MatchInfo - Change On Scene 3.txt",
    "listOfPaths": ["overlayText1path", "overlayText2path", "overlayText3path", "overlayText4path", "overlayText5path", "overlayText6path"],

    "gameUrl": "http://localhost:6119/game",
    "uiUrl": "http://localhost:6119/ui",
    "unmaskedUrl": "http://sc2unmasked.com/API/Player?",

    "mmr": "0",
    "updatedMmrThisGame": False,
    "apiCallDoneThisGame": False,
    "titleLast": "",
    "titleCurrent": "",

    "gameResponse": {},
    "uiResponse": {},
    "sc2ApiResponseDone": 0,
    "updatedGameApiData": 0,

    "updateInterval": 5,
    "mmrUpdateInterval": 5,

    "timeSinceLastUpdate": time.time(),
    "timeSinceLastMMRupdate": 0,
    "latestApiUpdateTimestamp": 0,

    "prevP1Name": "",
    # "prevP2Name": "", # not used (yet?)
}
apiData = defaultdict(lambda: "")
settings = {}
variables = {
    "$matchup": "",
    "$gamemins": "",
    "$gamesecs": "",
    "$p1race": "",
    "$p1Race": "",
    "$p2race": "",
    "$p2Race": "",
    "$p1name": "",
    "$p2name": "",
    "$p1mmr": "",
    "$p2mmr": "",
    "$p2url": "",
    "$server": "",
    "$Server": "",
}
raceLongName = {
    "Z": "Zerg",
    "T": "Terran",
    "P": "Protoss",
    "R": "Random",
}

def Init():
    global matchInfo, settings, gameUrl, uiUrl

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
        settings["inGameIds"] = []
        settings["inGameIds"].append(settings["bnetUsername1"].lower())
        settings["inGameIds"].append(settings["bnetUsername2"].lower())
        settings["inGameIds"].append(settings["bnetUsername3"].lower())
        settings["inGameIds"].append(settings["bnetUsername4"].lower())
        settings["inGameIds"].append(settings["bnetUsername5"].lower())
        settings["inGameIds"].append(settings["bnetUsername6"].lower())
        settings["inGameIds"].append(settings["bnetUsername7"].lower())
        settings["inGameIds"].append(settings["bnetUsername8"].lower())
        settings["inGameIds"].append(settings["bnetUsername9"].lower())
        settings["inGameIds"].append(settings["bnetUsername10"].lower())
        settings["channel"] = Parent.GetChannelName()

        if settings["gamingPcIp"] != "":
            gameUrl = "http://{}/game".format(settings["gamingPcIp"])
            uiUrl = "http://{}/ui".format(settings["gamingPcIp"])

        # create empty overlay files
        Unload(onlyCreateFiles=True)

        # INIT LOGGING
        try:
            os.makedirs(os.path.join(path, "Logs"))
        except: pass
        if settings["devDebugLogging"]:        
            loggingLevel = logging.DEBUG
            # matchInfo["logger"].debug('debug message')
            # matchInfo["logger"].info('info message')
            # matchInfo["logger"].warn('warn message')
            # matchInfo["logger"].error('error message')
            # matchInfo["logger"].critical('critical message')
        else:
            loggingLevel = logging.INFO

        try:
            matchInfo["logger"] = logging.getLogger('SC2MatchInfo')
            formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
            logFileName = datetime.datetime.now().strftime('%Y_%m_%d.log')
            matchInfo["filerHandler"] = logging.FileHandler(os.path.join(path, "Logs", logFileName), mode='a')
            matchInfo["filerHandler"].setFormatter(formatter)
            # fileHandler = logging.FileHandler(os.path.join(path, "Logs", logFileName), mode='a')
            # fileHandler.setFormatter(formatter)
            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(formatter)

            matchInfo["logger"].setLevel(loggingLevel)
            matchInfo["logger"].addHandler(matchInfo["filerHandler"])
            matchInfo["logger"].addHandler(streamHandler)  
        except:
            Debug("Could not start logging to file. Permission error.")
        
        matchInfo["logger"].debug("MatchInfo Initialized with settings: {}".format(json.dumps({
            key: settings[key] for key in ["chosenServer", "findOpponentMmrOption", "enableUnbarcoder", "enabledTitleUpdater","enabledOverlayUpdater", "enableStreamerShoutout", "postOpponentLinkInChat", "titleInMenu", "titleInGameAsPlayer", "titleInGameAsCaster", "titleInGameAsOther", "titleIn1v1Replay", "enableStreamerShoutout", "postOpponentLinkInChat", "bnetUsername1", "bnetUsername2", "bnetUsername3", "bnetUsername4", "bnetUsername5", "bnetUsername6", "bnetUsername7", "bnetUsername8", "bnetUsername9", "bnetUsername10", "gamingPcIp", "streamerBlacklist"]
        }, indent=4, sort_keys=True)))        

        settings["configFileLoaded"] = True
    except Exception as e:
        Parent.Log("SC2MatchInfo", "Error during the Init() function, error: {}".format(e))
        return
    return


#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
    Init()
    return

def ScriptToggled(state):
    global matchInfo
    if not state:
        # unload logger so files can be removed
        matchInfo["logger"].setLevel(logging.WARNING)
        matchInfo["logger"].removeHandler(matchInfo["filerHandler"])
        matchInfo["filerHandler"].close()

#---------------------------------------
#    [Required] Tick Function
#---------------------------------------
def Tick():
    global matchInfo, variables, settings

    t1 = time.time()
    if settings.get("configFileLoaded", False):
        if t1 - matchInfo["timeSinceLastMMRupdate"] > matchInfo["mmrUpdateInterval"] and apiData["inStarcraftLocation"] == "1v1AsPlayer" and not matchInfo["updatedMmrThisGame"] and matchInfo["apiCallDoneThisGame"]:
            matchInfo["logger"].debug("Streamer went into a new match: {} ({}) against {} ({})".format(variables["$p1name"], variables["$p1race"], variables["$p2name"], variables["$p2race"]))
            matchInfo["timeSinceLastMMRupdate"] = t1
            matchInfo["updatedMmrThisGame"] = True
            GetMmrWrapperFunction()
            # threading.Thread(target=GetMmrWrapperFunction, args=()).start()
        elif matchInfo["updatedMmrThisGame"] and apiData["inStarcraftLocation"] != "1v1AsPlayer":
            matchInfo["logger"].debug("Streamer went into the menu.")
            matchInfo["updatedMmrThisGame"] = False
            matchInfo["apiCallDoneThisGame"] = False

        if t1 - matchInfo["timeSinceLastUpdate"] > matchInfo["updateInterval"]:
            matchInfo["timeSinceLastUpdate"] = t1
            response = GetSc2ApiResponse()
            if response:
                threading.Thread(target=UpdateTwitchTitle, args=()).start()
    return


def GetSc2ApiResponse():
    global matchInfo
    try:
        gameResponse = json.loads(json.loads(Parent.GetRequest(matchInfo["gameUrl"], {}))['response'])
        uiResponse = json.loads(json.loads(Parent.GetRequest(matchInfo["uiUrl"], {}))['response'])

        time1 = time.time()
        if matchInfo["latestApiUpdateTimestamp"] < time1:
            matchInfo["latestApiUpdateTimestamp"] = time1
            if ProcessClientApiData(gameResponse, uiResponse):
                return True
    except Exception as e:
        # Parent.Log("SC2MatchInfo", "Starcraft is not running.")
        pass
    return False


def ProcessClientApiData(gameResponse, uiResponse):
    global apiData, matchInfo, settings, variables
    try:
        if len(gameResponse["players"]) == 2:
            apiData["player1Race"] = gameResponse["players"][0]["race"][0].upper()
            apiData["player2Race"] = gameResponse["players"][1]["race"][0].upper()
            apiData["player1Name"] = gameResponse["players"][0]["name"]
            apiData["player2Name"] = gameResponse["players"][1]["name"]
            apiData["player1Result"] = gameResponse["players"][0]["result"].lower()
            apiData["player2Result"] = gameResponse["players"][1]["result"].lower()
            apiData["ingameMins"], apiData["ingameSecs"] = divmod(int(gameResponse["displayTime"]), 60)

            # if both player names are detected in settings["inGameIds"]
            # then choose the streamer to be the player who had that player1Name in the last match
            if apiData["player1Name"].lower() in settings["inGameIds"] and apiData["player2Name"].lower() in settings["inGameIds"] and matchInfo["prevP1Name"] in [apiData["player1Name"], apiData["player2Name"]]:
                apiData["streamerIsInValid1v1Game"] = True
                if apiData["player1Name"] == matchInfo["prevP1Name"]:
                    pass
                elif apiData["player2Name"] == matchInfo["prevP1Name"]:
                    apiData["player1Race"], apiData["player2Race"] = apiData["player2Race"], apiData["player1Race"]
                    apiData["player1Name"], apiData["player2Name"] = apiData["player2Name"], apiData["player1Name"]
                    apiData["player1Result"], apiData["player2Result"] = apiData["player2Result"], apiData["player1Result"]

            elif apiData["player1Name"].lower() in settings["inGameIds"]:
                apiData["streamerIsInValid1v1Game"] = True
            elif apiData["player2Name"].lower() in settings["inGameIds"]:
                apiData["player1Race"], apiData["player2Race"] = apiData["player2Race"], apiData["player1Race"]
                apiData["player1Name"], apiData["player2Name"] = apiData["player2Name"], apiData["player1Name"]
                apiData["player1Result"], apiData["player2Result"] = apiData["player2Result"], apiData["player1Result"]
                apiData["streamerIsInValid1v1Game"] = True
            else:
                apiData["streamerIsInValid1v1Game"] = False

            # cache player names for next game in case both player names are in the settings["inGameIds"] list
            matchInfo["prevP1Name"] = apiData["player1Name"]

            apiData["matchup"] = apiData["player1Race"] + "v" + apiData["player2Race"]

            variables = {
                "$matchup": apiData["matchup"],
                "$gamemins": str(apiData["ingameMins"]),
                "$gamesecs": str(apiData["ingameSecs"]),
                "$p1race": apiData["player1Race"],
                "$p1Race": raceLongName[apiData["player1Race"]],
                "$p2race": apiData["player2Race"],
                "$p2Race": raceLongName[apiData["player2Race"]],
                "$p1name": apiData["player1Name"],
                "$p2name": variables["$p2name"] if matchInfo["apiCallDoneThisGame"] else apiData["player2Name"],
                "$p1mmr": variables["$p1mmr"],
                "$p2mmr": variables["$p2mmr"],
                "$server": variables["$server"],
                "$Server": variables["$Server"],
            }

        if uiResponse["activeScreens"] == []:
            if len(gameResponse["players"]) == 2:
                if gameResponse["isReplay"]:
                    apiData["inStarcraftLocation"] = "1v1Replay"
                    matchInfo["titleCurrent"] = ReplaceVariables(settings["titleIn1v1Replay"])
                else:
                    if apiData["streamerIsInValid1v1Game"]:
                        apiData["inStarcraftLocation"] = "1v1AsPlayer"
                        matchInfo["titleCurrent"] = ReplaceVariables(settings["titleInGameAsPlayer"])
                    else:
                        apiData["inStarcraftLocation"] = "1v1AsCaster"
                        matchInfo["titleCurrent"] = ReplaceVariables(settings["titleInGameAsCaster"])
            else:
                apiData["inStarcraftLocation"] = "other"
                matchInfo["titleCurrent"] = ReplaceVariables(settings["titleInGameAsOther"])
        else:
            apiData["inStarcraftLocation"] = "menu"
            matchInfo["titleCurrent"] = ReplaceVariables(settings["titleInMenu"])

        matchInfo["apiCallDoneThisGame"] = True
        return True

    except Exception as e:
        matchInfo["logger"].error("Error processing data from the SC2 Client API, error: {}".format(e))
    return False


def ReplaceVariables(string):
    global variables
    for variable, text in variables.items():
        string = string.replace(variable, str(text))
    return string


def UpdateTwitchTitle():
    global matchInfo, settings, apiData

    if settings["enabledTitleUpdater"] and matchInfo["titleLast"] != matchInfo["titleCurrent"]:
        try:
            matchInfo["titleLast"] = matchInfo["titleCurrent"]
            headers = {
                "Accept": "application/vnd.twitchtv.v5+json",
                "Client-ID":
                "hfhxpd5q6d7lxwmmi849rm7qprcktw",
                "Authorization": "OAuth {}".format(settings["oauth"].strip())
            }
            r = json.loads(
                Parent.GetRequest("https://decapi.me/twitch/id/" + Parent.GetChannelName(), {}))

            if r["status"] == 200:
                streamerId = r["response"]
                payload = {
                    "channel": {
                        "status": matchInfo["titleCurrent"],
                        "game": "StarCraft II"
                    }
                }
                r = Parent.PutRequest(
                    "https://api.twitch.tv/kraken/channels/" + streamerId,
                    headers, payload, True)
                pr = json.loads(r)
                if pr["status"] == 200:
                    # Parent.Log("SC2MatchInfo", "Successfully updated channel status and game.")
                    pass

        except Exception as e:
            matchInfo["logger"].error("Error trying to update twitch title, error: {}".format(e))

    if settings["enabledOverlayUpdater"]:
        writeOverlayFile("overlayText1")
        writeOverlayFile("overlayText2")
        writeOverlayFile("overlayText3")
        writeOverlayFile("overlayText4", True)
        writeOverlayFile("overlayText5", True)
        writeOverlayFile("overlayText6", True)
    return

def Execute(data):
    return

def Unload(onlyCreateFiles=False):
    global matchInfo
    path = os.path.dirname(__file__)

    for file in matchInfo["listOfPaths"]:
        # create the "Overlay" subfolder if it doesnt exist
        if not os.path.exists(os.path.dirname(os.path.join(path, matchInfo[file]))):
            os.makedirs(os.path.dirname(os.path.join(path, matchInfo[file])))
        # create text files in "Overlay" subfolder
        if onlyCreateFiles and not os.path.exists(os.path.join(path, matchInfo[file])):
            with codecs.open(os.path.join(path, matchInfo[file]), encoding='utf-8-sig', mode='w+') as file:
                file.write(" ")
        # empty files at streamlabs chatbot shutdown
        elif not onlyCreateFiles:
            with codecs.open(os.path.join(path, matchInfo[file]), encoding='utf-8-sig', mode='w+') as file:
                file.write(" ")
    return


def OpenOauthLink():
    os.startfile("http://brains-world.eu/sl-chatbot/twitch-oauth-token-generator/")

def OpenVariables():
    os.startfile("http://brains-world.eu/chatbot-starcraft-scripts-variables/")

def Debug(message):
    if debuggingMode:
        Parent.Log("SC2MatchInfo", message)

def writeOverlayFile(variableName="overlayText1", isOnSceneChange=False):
    global settings, matchInfo
    path = os.path.dirname(__file__)

    if isOnSceneChange:
        chooseTextDict = {
            "menu": "1",
            "1v1AsPlayer": "2",
            "1v1AsCaster": "3",
        }
        loc = apiData["inStarcraftLocation"]
        addition = chooseTextDict[loc]
    else:
        addition = ""

    if matchInfo[variableName + "Written"] != ReplaceVariables(
            settings[variableName + addition]):
        matchInfo[variableName + "Written"] = ReplaceVariables(
            settings[variableName + addition])
        try:
            # create the "Overlay" subfolder if it doesnt exist
            if not os.path.exists(os.path.dirname(os.path.join(path,matchInfo[variableName + "path"]))):
                os.makedirs( os.path.dirname( os.path.join(path, matchInfo[variableName + "path"])))

            with codecs.open(os.path.join(path, matchInfo[variableName + "path"]), encoding='utf-8-sig', mode='w+') as file:
                file.write(matchInfo[variableName + "Written"])
        except Exception as e:
            Parent.Log("Error trying to write overlay text files, error: {}".format(e))


def ReceiveSc2UnmaskedResponse(url, params={"stream": "burnysc2"}):
    # make the getRequest string, e.g.: name=Brain&race=z&server=eu
    paramAsString = "&".join([a + "=" + b for a, b in zip(params.keys(), params.values())])
    unmaskedResponse = json.loads(Parent.GetRequest(url + paramAsString, {}))

    if unmaskedResponse["status"] == 200:
        return json.loads(unmaskedResponse["response"])["players"]
    else:
        matchInfo["logger"].error("Error receiving data from sc2unmasked.com")
        return []

def GetMmrWrapperFunction():
    GetMmrFromSc2Unmasked()
    if settings["enabledOverlayUpdater"]:
        writeOverlayFile("overlayText1")
        writeOverlayFile("overlayText2")
        writeOverlayFile("overlayText3")
        writeOverlayFile("overlayText4", True)
        writeOverlayFile("overlayText5", True)
        writeOverlayFile("overlayText6", True)

def GetMmrFromSc2Unmasked():
    global matchInfo, apiData, variables, settings
    if apiData["inStarcraftLocation"] != "1v1AsPlayer":
        return

    variables["$p2name"] = apiData["player2Name"]
    variables["$p2url"] = ""
    variables["$p2mmr"] = "unknown"

    parameters = {
        "mode": "LOTV_SOLO",
        "name": apiData["player1Name"],
        "race": raceLongName[apiData["player1Race"]].lower(),
        "stream": Parent.GetChannelName().lower()
    }
    if settings["chosenServer"] != "Auto":
        parameters["server"] = settings["chosenServer"].lower()
        variables["$server"] = settings["chosenServer"].lower()
        variables["$Server"] = settings["chosenServer"].upper()

    response = ReceiveSc2UnmaskedResponse(matchInfo["unmaskedUrl"], parameters)
    if len(response) == 0:  # no results found, expanding the search (e.g. if stream url is not listed)
        parameters.pop("stream", None)
        response = ReceiveSc2UnmaskedResponse(matchInfo["unmaskedUrl"], parameters)

    if len(response) == 0:
        matchInfo["logger"].debug("The streamer was not found on SC2Unmasked. Reasons: Not ranked yet, playing unranked or wrong server selected (The sc2unmasked website updates every 10-20 minutes.")
        return

    elif len(response) == 1:  # perfect match, assuming stream url and nickname are properly linked
        streamerInfo = response[0]
        variables["$p1mmr"] = streamerInfo["mmr"]
        variables["$server"] = streamerInfo["server"]
        variables["$Server"] = streamerInfo["server"].upper()
        matchInfo["logger"].debug("The streamer was found on SC2Unmasked. MMR: {}, Server: {}".format(variables["$p1mmr"], variables["$Server"]))

    elif len(response) > 1:  # too many results found, choose the player with the most recent match history
        responseSorted = sorted(response, key=lambda x: int(x["last_played"].strip("\/Date(").strip(")\/")), reverse=True)  # "lastplayed" only tracks ranked game
                
        streamerInfo = responseSorted[0]
        variables["$p1mmr"] = streamerInfo["mmr"]
        variables["$server"] = streamerInfo["server"]
        variables["$Server"] = streamerInfo["server"].upper()
        matchInfo["logger"].debug("{} accounts with the same name as the streamer were found. The account with the most recent match played was selected. MMR: {}, Server: {}".format(len(response), variables["$p1mmr"], variables["$Server"]))

    # assuming the data above was received and matched correctly, now trying to figure out the MMR of the opponent
    if " " in apiData["player2Name"]:
        matchInfo["logger"].debug("Streamer is playing against AI.")
        return

    opponentParams = {
        "mode": "LOTV_SOLO",
        "name": apiData["player2Name"],
        "race": raceLongName[apiData["player2Race"]].lower(),
        "server": variables["$server"],  # variable is available at this point
    }

    oppoResponse = ReceiveSc2UnmaskedResponse(matchInfo["unmaskedUrl"], opponentParams)
    # filter out opponents that havent played ladder in 14 days #TODO: need to check if i need to increase or lower the threshold
    if settings["findOpponentMmrOption"] == "Closest MMR":
        oppoResponse = [x for x in oppoResponse if time.time() - int(x["last_played"].strip("\/Date(").strip(")\/")) / 1000 < 14*24*60*60]

    if len(oppoResponse) == 0:  # opponent not listed on sc2unmasked - hes playing unranked?
        variables["$p2mmr"] = "0"
        variables["$p2url"] = ""
        matchInfo["logger"].debug("The opponent was not found on sc2unmasked. Most likely reason is he did not play his placement match yet or he plays only unranked (the sc2unmasked website updates every 10-20 minutes.")
        return
    elif len(oppoResponse) == 1:  # opponent found
        opponentInfo = oppoResponse[0]
        matchInfo["logger"].debug("The opponent was exactly found once on sc2unmasked, a perfect match (if he is playing ranked).")
    elif len(oppoResponse) > 1:  # too many opponents under this name listed
        # options:
        # - pick the one with the closest mmr to streamer
        # - pick the one with the most recent match played
        matchInfo["logger"].debug("{} accounts with the same name of the opponent were found.".format(len(oppoResponse)))
        if settings["findOpponentMmrOption"] == "Closest MMR":            
            responseSorted = sorted(
                oppoResponse,
                key=lambda x: abs(int(variables["$p1mmr"]) - int(x["mmr"])))
            opponentInfo = responseSorted[0]
        elif settings["findOpponentMmrOption"] == "Most Recent Activity":
            responseSorted = sorted(oppoResponse, key=lambda x: int(x["last_played"].strip("\/Date(").strip(")\/")), reverse=True)
            opponentInfo = responseSorted[0]
        

    variables["$p2mmr"] = opponentInfo["mmr"]
    matchInfo["logger"].debug("The opponent's MMR has been identified as {} mmr.".format(variables["$p2mmr"]))

    if settings["enableUnbarcoder"]: # replace opponent name with display name if available
        if opponentInfo["display_name"] != None:
            variables["$p2name"] = opponentInfo["display_name"]
            matchInfo["logger"].debug("The opponent has a display name (unbarcoding / smurf). Info about opponent:")
        else:
            matchInfo["logger"].debug("The opponent does not have a display name. Info about opponent:")
    else:
        matchInfo["logger"].debug("Info about opponent:")
    # if opponentIsBarcode and opponentInfo["display_name"] != None:
    #     variables["$p2name"] = opponentInfo["display_name"]
    #     matchInfo["logger"].debug("The opponent is a barcode. Info about opponent:")
    # elif opponentIsBarcode:
    #     matchInfo["logger"].debug("The opponent is a barcode but not identified on SC2Unmasked. Info about opponent:")
    # else:
    #     matchInfo["logger"].debug("The opponent uses a name. Info about opponent:")

    matchInfo["logger"].debug("{}".format(json.dumps({
        "Name": apiData["player2Name"],
        "Race": raceLongName[apiData["player2Race"]].lower(),
        "SC2Unmasked API url": matchInfo["unmaskedUrl"] + "&".join([a + "=" + b for a, b in zip(opponentParams.keys(), opponentParams.values())]),
        "SC2Unmasked display name": opponentInfo["display_name"],
        "SC2Unmasked account name": opponentInfo["acc_name"],
        "SC2Unmasked stream is online": opponentInfo["is_online"],
        "SC2Unmasked stream url": "http://{}/{}".format(opponentInfo["platform"], opponentInfo["stream_name"]),
    }, indent=4, sort_keys=True)))

    if opponentInfo["stream_name"] != None:
        variables["$p2url"] = "http://{}/{}".format(opponentInfo["platform"], opponentInfo["stream_name"])
    else:
        variables["$p2url"] = ""
    
    settings["streamerBlacklist"] = settings["streamerBlacklist"].lower().strip(",").replace(" ","").split(",")
    if settings["streamerBlacklist"] == [""]:
        settings["streamerBlacklist"] = []

    if opponentInfo["is_online"] and settings["postOpponentLinkInChat"].strip(" ") != "" and settings["enableStreamerShoutout"] and opponentInfo["stream_name"] not in settings["streamerBlacklist"]:
        if opponentInfo["platform"].lower() == "twitch.tv" and settings["useMultitwitch"]:
            # replace with multitwitch if opponent is streaming on twitch
            variables["$p2url"] = "http://www.multitwitch.tv/{}/{}".format(Parent.GetChannelName().lower(), opponentInfo["stream_name"])        
        # http://www.multitwitch.tv/gunnermaniac3/narcissawright
        Parent.SendStreamMessage(ReplaceVariables(settings["postOpponentLinkInChat"]))
    return


def BtnOpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

def BtnOpenOverlayFilesFolder():
    """Open the folder where the overlay text files are saved in"""
    location = os.path.join(os.path.dirname(__file__), "Overlay")
    os.startfile(location)
    return

def OpenLogFolder():
    location = os.path.join(os.path.dirname(__file__), "Logs")
    os.startfile(location)
    return