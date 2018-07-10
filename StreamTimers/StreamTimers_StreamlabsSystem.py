#---------------------------------------
#   Import Libraries
#---------------------------------------
import sys
import clr
import time
import os
import json
import threading
import codecs
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
debuggingMode = True
ScriptName = "StreamTimers"
Website = "http://www.brains-world.eu"
Description = "Uptime & Countdown with UI Interface"
Creator = "Brain & Burny"
Version = "1.1.4"

configFile = "settings.json"
path = os.path.dirname(__file__)
timeFromLastTick = time.time()
countdown = {
    "oldCountdownText": "",
    "countdownText": "",
    "countdownFileName": "Overlay\Countdown.txt",
    "countdownJsonFileName": "Countdown.json",
    "currentCountdownTime": 0,
    "countdownIsRunning": False,
}
cdVariables = {
    "$h$": 0,
    "$m$": 0,
    "$s$": 0,
    "$hh$": "0",
    "$mm$": "0",
    "$ss$": "0",
}
uptime = {
    "oldUptimeText": "",
    "uptimeText": "",
    "uptimeFileName": "Overlay\Uptime.txt",
    "uptimeJsonFileName": "Uptime.json",
    "currentUptime": 0,
    "twitchApiResponseOffline": 0,
}
utVariables = {
    "$h$": 0,
    "$m$": 0,
    "$s$": 0,
    "$hh$": "0",
    "$mm$": "0",
    "$ss$": "0",
}

settings = {}
countdownThreadActive = False
uptimeThreadActive = False
threadsKeepAlive = True

#---------------------------------------
#   [Required] Initialize Data / Load Only
#---------------------------------------


def Init():
    global configFile, path, settings, uptimeThreadActive, uptime, utVariables
    path = os.path.dirname(__file__)

    # create subfolder if it doesnt exist
    if not os.path.exists(os.path.dirname(os.path.join(path, countdown["countdownFileName"]))):
        os.makedirs(os.path.dirname(os.path.join(path, countdown["countdownFileName"])))
    # if not os.path.exists(os.path.dirname(os.path.join(path, uptime["uptimeFileName"]))):
    #     os.makedirs(os.path.dirname(os.path.join(path, uptime["uptimeFileName"])))

    # create overlay files if they dont exist
    if not os.path.exists(os.path.join(path, countdown["countdownFileName"])):
        with open(os.path.join(path, countdown["countdownFileName"]), "w+") as f:
            f.write(" ")
    if not os.path.exists(os.path.join(path, uptime["uptimeFileName"])):
        with open(os.path.join(path, uptime["uptimeFileName"]), "w+") as f:
            f.write(" ")

    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
    except:
        settings = {
            "cdInterval": 6,
            "cdTimeFormat": "$mm$:$ss$",
            "cdCustomText": "Countdown done. Starting soon.",
            "cbCustomUptimeText": True,
            "customUptimeText": "$h$:$mm$:$ss$",
            "maxSleepTimer": 10.0,
        }


    # load countdown from json file
    try:
        path = os.path.dirname(__file__)
        with codecs.open(os.path.join(path, countdown["countdownJsonFileName"]), encoding='utf-8-sig', mode='r') as file:
            countdown["currentCountdownTime"] = json.load(file, encoding='utf-8-sig')["currentCountdownTime"]
            if countdown["currentCountdownTime"] > 0:
                StartCountdown()
    except:
        pass

    # load uptime from json file
    try:
        path = os.path.dirname(__file__)
        with codecs.open(os.path.join(path, uptime["uptimeJsonFileName"]), encoding='utf-8-sig', mode='r') as file:
            uptime["currentUptime"] = json.load(file, encoding='utf-8-sig')["currentUptime"]
    except:
        pass

    if not uptimeThreadActive and not Parent.IsLive():
        uptime["currentUptime"] = 0
        SetUptimeVariables()
        WriteUptimeToFile()

    return


#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
    global settings, cdVariables, countdown, uptime, utVariables

    if data.IsChatMessage():
        # sets new countdown and starts it
        if data.GetParamCount() == 2 and data.GetParam(0).lower() == settings["cdSetCountdown"].lower():
            if Parent.HasPermission(data.User, "Caster", ""):
                try:
                    countdown["currentCountdownTime"] = int(
                        data.GetParam(1)) * 60
                    if not countdown["countdownIsRunning"]:
                        StartCountdown()
                    if settings["cdShowCountdownResponse"]:
                        Parent.SendTwitchMessage(
                            ("New countdown set to " + AutoFormat(*ConvertSecondsToHMS(int(data.GetParam(1)) * 60)))[:490])
                except ValueError:
                    if settings["cdShowCountdownResponse"]:
                        Parent.SendTwitchMessage(
                            ("Incorrect usage. Write " + settings["cdSetCountdown"] + " <seconds> to set new the countdown.")[:490])

        # sets a custom uptime
        if data.GetParamCount() == 2 and data.GetParam(0).lower() == settings["setUptime"].lower():
            if Parent.HasPermission(data.User, "Caster", ""):
                try:
                    uptime["currentUptime"] = int(data.GetParam(1)) * 60
                    SetUptimeVariables()
                    WriteUptimeToFile()
                    if settings["showUptimeResponse"]:
                        Parent.SendTwitchMessage(
                            ("Uptime set to " + AutoFormat(*ConvertSecondsToHMS(int(data.GetParam(1)) * 60)))[:490])
                except ValueError:
                    if settings["showUptimeResponse"]:
                        Parent.SendTwitchMessage(
                            ("Incorrect usage. Write " + settings["setUptime"] + " <seconds> to set the uptime.")[:490])


#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
    Init()
    return


def StartCountdown():
    global countdown, settings, countdownThreadActive

    countdown["currentCountdownTime"] = settings["cdInterval"] * 60
    countdown["oldCountdownText"] = " "
    with codecs.open(os.path.join(path, countdown["countdownFileName"]), encoding='utf-8-sig', mode='w+') as file:
        file.write(" ")
    with codecs.open(os.path.join(path, countdown["countdownJsonFileName"]), encoding='utf-8-sig', mode='w+') as file:
        json.dump({"currentCountdownTime": 0}, file)

    countdown["countdownIsRunning"] = True
    if not countdownThreadActive:
        threading.Thread(target=CountdownThread, args=()).start()


def CountdownThread():
    global cdVariables, countdown, settings, timeFromLastTick, countdownThreadActive, threadsKeepAlive
    countdownThreadActive = True

    while countdown["countdownIsRunning"] and threadsKeepAlive:
        countdown["currentCountdownTime"] -= 1
        tempMinutes, tempSeconds = divmod(
            countdown["currentCountdownTime"], 60)
        tempHours, tempMinutes = divmod(tempMinutes, 60)
        cdVariables["$h$"] = str(int(tempHours))
        cdVariables["$m$"] = str(int(tempMinutes))
        cdVariables["$s$"] = str(int(tempSeconds))
        cdVariables["$hh$"] = str(int(tempHours)).zfill(2)
        cdVariables["$mm$"] = str(int(tempMinutes)).zfill(2)
        cdVariables["$ss$"] = str(int(tempSeconds)).zfill(2)

        cdVariables["$autoFormat$"] = AutoFormat(
            cdVariables["$h$"], cdVariables["$m$"], cdVariables["$s$"])

        countdown["countdownText"] = FormatCountdownString(
            settings["cdTimeFormat"])

        #Debug(settings["cdTimeFormat"] + " " + countdown["countdownText"])

        if countdown["currentCountdownTime"] < 0:
            countdown["countdownText"] = settings["cdCustomText"]
            countdown["countdownIsRunning"] = False

        if countdown["oldCountdownText"] != countdown["countdownText"]:
            # write countdown to overlay file
            with codecs.open(os.path.join(path, countdown["countdownFileName"]), encoding='utf-8-sig', mode="w+") as file:
                file.write(countdown["countdownText"])
            # write countdown to json file in case of "reload scripts" or streamlabs chatbot is shut down
            with codecs.open(os.path.join(path, countdown["countdownJsonFileName"]), encoding='utf-8-sig', mode='w+') as file:
                json.dump({"currentCountdownTime": countdown["currentCountdownTime"]}, file)
            countdown["oldCountdownText"] = countdown["countdownText"]
        time.sleep(1)
    countdownThreadActive = False


def FormatCountdownString(string):
    global cdVariables, countdown
    for variable, text in cdVariables.items():
        string = string.replace(variable, text)
    return string


def ResetUptime():
    global uptime, settings
    uptime["currentUptime"] = 0
    uptime["twitchApiResponseOffline"] = 0
    with codecs.open(os.path.join(path, uptime["uptimeFileName"]), encoding='utf-8-sig', mode='w+') as file:
        file.write(" ")
    with codecs.open(os.path.join(path, uptime["uptimeJsonFileName"]), encoding='utf-8-sig', mode='w+') as file:
        json.dump({"currentUptime": uptime["currentUptime"]}, file)


def UptimeThread():
    global utVariables, uptime, uptimeThreadActive, threadsKeepAlive

    uptimeThreadActive = True
    while uptime["twitchApiResponseOffline"] < (settings["maxSleepTimer"] * 60) and threadsKeepAlive:
        if Parent.IsLive():
            uptime["twitchApiResponseOffline"] = 0
        else:
            uptime["twitchApiResponseOffline"] += 1

        # once the "Max Sleep Timer" has been reached, it will reset the uptime to 0:00:00
        if uptime["twitchApiResponseOffline"] >= (settings["maxSleepTimer"] * 60):
            uptime["currentUptime"] = 0
        else:
            uptime["currentUptime"] += 1

        SetUptimeVariables()
        WriteUptimeToFile()
        time.sleep(1)

    uptimeThreadActive = False


def SetUptimeVariables():
    global utVariables, settings, uptime
    utVariables["$m$"], utVariables["$s$"] = divmod(
        uptime["currentUptime"], 60)
    utVariables["$h$"], utVariables["$m$"] = divmod(utVariables["$m$"], 60)

    utVariables["$h$"] = int(utVariables["$h$"])
    utVariables["$m$"] = int(utVariables["$m$"])
    utVariables["$s$"] = int(utVariables["$s$"])

    utVariables["$hh$"] = str(utVariables["$h$"]).zfill(2)
    utVariables["$mm$"] = str(utVariables["$m$"]).zfill(2)
    utVariables["$ss$"] = str(utVariables["$s$"]).zfill(2)

    utVariables["$autoFormat$"] = AutoFormat(
        utVariables["$h$"], utVariables["$m$"], utVariables["$s$"])

    uptime["uptimeText"] = FormatUptimeString(settings["customUptimeText"])


def WriteUptimeToFile():
    global uptime
    if uptime["uptimeText"] != uptime["oldUptimeText"]:
        with codecs.open(os.path.join(path, uptime["uptimeJsonFileName"]), encoding='utf-8-sig', mode='w+') as file:
            json.dump({"currentUptime": uptime["currentUptime"]}, file)

        with codecs.open(os.path.join(path, uptime["uptimeFileName"]), encoding='utf-8-sig', mode='w+') as file:
            file.write(uptime["uptimeText"])

        uptime["oldUptimeText"] = uptime["uptimeText"]


def FormatUptimeString(string):
    global utVariables, uptime
    for variable, text in utVariables.items():
        string = string.replace(variable, str(text))
    return string


def ConvertSecondsToHMS(seconds):
    secs = int(seconds)
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return hours, mins, secs


def AutoFormat(hours, minutes, seconds):
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    returnString = ""
    seperator = ":"
    if hours > 0:
        returnString += str(hours) + seperator
        returnString += str(minutes).zfill(2) + seperator
        returnString += str(seconds).zfill(2)
    else:
        if minutes > 0:
            returnString += str(minutes) + seperator
            returnString += str(seconds).zfill(2)
        else:
            returnString += str(seconds)
    return returnString

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------


def Tick():
    global uptimeThreadActive
    if not uptimeThreadActive and Parent.IsLive():
        uptimeThreadActive = True
        threading.Thread(target=UptimeThread, args=()).start()
    return


def ScriptToggled(state):
    global threadsKeepAlive
    # if enabled again tell the script to keep the threads running again
    if state:
        threadsKeepAlive = True
    # if the script gets disabled, stop all timers and resets the textfiles
    else:
        ResetUptime()
        uptime["twitchApiResponseOffline"] = 0
        Unload()
    return


def Unload():
    global threadsKeepAlive
    threadsKeepAlive = False
    return

def OpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

def BtnOpenOverlayFolder():
    """Open the folder where the user can find the index.html"""
    location = os.path.join(os.path.dirname(__file__), "Overlay")
    os.startfile(location)
    return


def Debug(message):
    if debuggingMode:
        Parent.Log("StreamTimers", message)
