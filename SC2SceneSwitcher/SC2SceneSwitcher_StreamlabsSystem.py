"""
###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
"""

#---------------------------------------
#	Import Libraries
#---------------------------------------
import sys
import datetime
import json
import os
import clr
import codecs
import threading

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "SCII - Scene Switcher"
Website = "https://www.brains-world.eu"
Description = "Scene Switcher for StarCraft II"
Creator = "Brain & Burny"
Version = "1.0.4"

#---------------------------------------
#	Set Variables
#---------------------------------------
debuggingMode = True
gameUrl = "http://localhost:6119/game"
uiUrl = "http://localhost:6119/ui"
configFile = "SC2SceneSwitcherConfig.json"
settings = {}
sceneSwitcher = {
    "checkThreadRunning": False,
}
currentScene = ""
lastSetScene = ""


#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
    global responseVariables, settings, configFile, gameUrl, uiUrl
    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
        settings["configFileLoaded"] = True
        if settings["gamingPcIp"] != "":
            gameUrl = "http://{}/game".format(settings["gamingPcIp"])
            uiUrl = "http://{}/ui".format(settings["gamingPcIp"])
    except:
        return
    return


def ReloadSettings(jsonData):
    Init()
    return


def Execute(data):
    return

def OpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

def OpenURL():
    os.startfile("https://obsproject.com/forum/resources/obs-websocket-remote-control-of-obs-studio-made-easy.466/")

def Tick():
    global sceneSwitcher, settings

    # if settings["isEnabled"]:
    if settings.get("configFileLoaded", False):
        if not sceneSwitcher["checkThreadRunning"]:
            sceneSwitcher["checkThreadRunning"] = True
            threading.Thread(target=PerformSceneSwitch, args=()).start()
    return


def PerformSceneSwitch():
    global gameUrl, uiUrl, settings, currentScene, lastSetScene, sceneSwitcher
    try:
        uiResponse = json.loads(json.loads(
            Parent.GetRequest(uiUrl, {}))['response'])
        gameResponse = json.loads(json.loads(
                    Parent.GetRequest(gameUrl, {}))['response'])

        currentScene = ""
        if settings["isCasterModeEnabled"]:
            # if uiResponse["activeScreens"] == [] or settings["switchAtLoadingScreen"] and uiResponse["activeScreens"] == ["ScreenLoading/ScreenLoading"]:
            if settings["switchAtLoadingScreen"] == "Switch at Game Start" and \
                uiResponse["activeScreens"] == [] or \
                \
                settings["switchAtLoadingScreen"] == "Switch at Loading Screen (1-2sec Delay)" and \
                (uiResponse["activeScreens"] == [] or \
                len(gameResponse["players"]) > 0 and \
                gameResponse["players"][0]["result"] == "Undecided" and \
                uiResponse["activeScreens"] == ["ScreenLoading/ScreenLoading"] and \
                gameResponse["displayTime"] == 0) or \
                \
                settings["switchAtLoadingScreen"] == "Switch at Loading Screen (ASAP)" and \
                (uiResponse["activeScreens"] == [] or \
                uiResponse["activeScreens"] == ["ScreenLoading/ScreenLoading"]) and \
                lastSetScene == settings["obsSceneInMenu"]:
                if gameResponse["isReplay"]:
                    currentScene = settings["obsSceneCasterInReplay"]
                else:
                    currentScene = settings["obsSceneCasterInGame"]
            else:
                currentScene = settings["obsSceneCasterInMenu"]
        else: 
            if settings["switchAtLoadingScreen"] == "Switch at Game Start" and \
                uiResponse["activeScreens"] == [] or \
                \
                settings["switchAtLoadingScreen"] == "Switch at Loading Screen (1-2sec Delay)" and \
                (uiResponse["activeScreens"] == [] or \
                len(gameResponse["players"]) > 0 and \
                gameResponse["players"][0]["result"] == "Undecided" and \
                uiResponse["activeScreens"] == ["ScreenLoading/ScreenLoading"] and \
                gameResponse["displayTime"] == 0) or \
                \
                settings["switchAtLoadingScreen"] == "Switch at Loading Screen (ASAP)" and \
                (uiResponse["activeScreens"] == [] or \
                uiResponse["activeScreens"] == ["ScreenLoading/ScreenLoading"]) and \
                lastSetScene == settings["obsSceneInMenu"]:
                if gameResponse["isReplay"]:
                    currentScene = settings["obsSceneInReplay"]
                else:
                    currentScene = settings["obsSceneInGame"]
            else:
                currentScene = settings["obsSceneInMenu"]

        if currentScene != "" and currentScene != lastSetScene:
            lastSetScene = currentScene
            #Parent.SetOBSCurrentScene(currentScene, callback)
            Parent.SetOBSCurrentScene(currentScene)

        sceneSwitcher["checkThreadRunning"] = False
    except Exception as e:
        sceneSwitcher["checkThreadRunning"] = False
        # TODO: a way to figure out how to display error message in case the streamer didnt connect ankhbbot with the OBS Remote plugin
        print("Unknown error while attempting to change scene", e)


def callback(string):
    Debug("error message: {}".format(string))


def Debug(message):
    if debuggingMode:
        Parent.Log("SceneSwitcher", message)
