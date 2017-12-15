#---------------------------------------
#	Import Libraries
#---------------------------------------
import sys
import clr
# import urllib2
import time
import datetime
import os
import json
import cgi
import codecs

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "TTS Queue"
Website = "https://burnysc2.github.io"
Creator = "Brain & Burny"
Version = "1.0.0"
Description = "Text-to-Speech Queue"
# Description = "Uses https://warp.world/scripts/tts-message to generate text-to-speech.\n\rSince there is no option to queue TTS commands, I made a script for it."

#---------------------------------------
#	Set Variables
#---------------------------------------
configFile = "TTSqueue.json"
users = {}

responseVariables = {
	"$user": "", # user name
	"$userPoints": "", # amount of currency the user has
	"$streamer": "", # name of the streamer
	"$currencyName": "", # channel currency
	"$pointsCost": "", # how many points tts command costs
	"$maxQueue": "", # how many tts entries per user there can be in a queue
	"$waitSeconds": "", # how many seconds have to pass before a user can queue a new tts command
	"$characterLimit": "", # max length of a tts entry
}

tts = {
	"queue": [],
	"timeUntilReady": 0,
	"timeOfLastTick": time.time(),
}

# https://warp.world/scripts/tts-message
voices = {  # https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
	"af": "Afrikaans Male",
	"sq": "Albanian Male",
	"ar": "Arabic Female",
	"hy": "Armenian Male",
	"aus": "Australian Female",
	"bs": "Bosnian Male",
	"pt2": "Brazilian Portuguese Female",
	"ca": "Catalan Male",
	"zh": "Chinese Female",
	"tai": "Chinese Taiwan Female",
	"hr": "Croatian Male",
	"cs": "Czech Female",
	"da": "Danish Female",
	"de": "Deutsch Female",
	"nl": "Dutch Female",
	"eo": "Esperanto Male",
	"fi": "Finnish Female",
	"fr": "French Female",
	"el": "Greek Female",
	"hi": "Hindi Female",
	"hu": "Hungarian Female",
	"is": "Icelandic Male",
	"id": "Indonesian Female",
	"it": "Italian Female",
	"ja": "Japanese Female",
	"ko": "Korean Female",
	"la": "Latin Female",
	"lv": "Latvian Male",
	"mk": "Macedonian Male",
	"ro": "Moldavian Male",
	"mo": "Montenegrin Male",
	#"no": "Norwegian Female", # disabled because it was super loud compared to the other voices
	"pl": "Polish Female",
	"pt": "Portuguese Female",
	"ro": "Romanian Male",
	"ru": "Russian Female",
	"sr": "Serbian Male",
	"srhr": "Serbo-Croatian Male",
	"sk": "Slovak Female",
	"es": "Spanish Female",
	"es2": "Spanish Latin American Female",
	"sw": "Swahili Male",
	"sv": "Swedish Female",
	"ta": "Tamil Male",
	"th": "Thai Female",
	"tr": "Turkish Female",
	"en": "UK English Female",
	"us": "US English Female",
	"vi": "Vietnamese Male",
	"cy": "Welsh Male",
}

#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------


def Init():
	global settings, voices, responseVariables
	path = os.path.dirname(__file__)

	with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
		settings = json.load(file, encoding='utf-8-sig')
	settings.update({
		"messageColor": "FFFD32",
		"fontColor": "FFFFFF",
		"fontSize": "13",
		"fontOutlineColor": "FFFFFF",
		"googleFont": "Roboto",
		"defaultVoice": "US English Female",
		"playAlert": "false",
	})
	voices[""] = settings["defaultVoice"]
	settings["randomKey"] = settings["randomKey"].strip() #removes whitespace left and right

	responseVariables["$streamer"] = Parent.GetDisplayName(Parent.GetChannelName())
	responseVariables["$currencyName"] = Parent.GetCurrencyName()
	responseVariables["$pointsCost"] = settings["userPointsCost"]
	responseVariables["$pointsCost"] = settings["userPointsCost"]
	responseVariables["$maxQueue"] = settings["userMaxQueues"]
	responseVariables["$waitSeconds"] = settings["userCooldown"]
	responseVariables["$characterLimit"] = settings["userMaxMessageLength"]
		
	return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	Init()
	return

#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	global tts, settings
	
	if settings["enabledTTS"]:
		if data.IsChatMessage():
			responseVariables["$user"] = Parent.GetDisplayName(data.User)
			responseVariables["$userPoints"] = Parent.GetPoints(data.User)
			
			messagesOfUser = [x for x in tts["queue"] if data.User == x["user"]]

			responseVariables["$userQueueEntries"] = len(messagesOfUser)

			# lists all languages when command "!ttshelp" is written
			if settings["command"].lower() + "help" == data.GetParam(0).lower():
				if settings["enableHelpCommand"] or Parent.HasPermission(data.User, "Caster", ""):
					languages = "Available languages/voices are: "
					for key,value in voices.items():
						languages += "{} ({})".format(value, key)
						# languages += value + "(" + key +  ")"
						languages += ", "
					languages = languages.rstrip(" ").rstrip(",")
					for i in range(len(languages) % 490):
						Parent.SendTwitchMessage(languages[i*490:490*(i+1)])

			elif settings["command"].lower() in data.GetParam(0).lower():
				message = " ".join(data.Message.split(" ")[1:])

				# only moderators allowed
				if True == settings["modsAllowedToUse"] != Parent.HasPermission(data.User, "moderator", ""):
					return

				# message too long
				if len(message) > settings["userMaxMessageLength"]:
					SendMessage(settings["responseMessageTooLong"])
					return

				# user has to wait to use TTS again
				lastUsage = users.get(data.User, 1)				
				if ConvertDatetimeToEpoch(datetime.datetime.now()) - settings["userCooldown"] < lastUsage:
					SendMessage(settings["responseUserSpamming"])
					return

				# user has too many TTS in queue
				if len(messagesOfUser) >= settings["userMaxQueues"]:
					SendMessage(settings["responseUserTooManyInQueue"])
					return

				# if user doesnt have enough points
				if Parent.GetPoints(data.User) < settings["userPointsCost"]:
					SendMessage(settings["responseUserNotEnoughPoints"])
					return
				
				# try to find voice
				voiceFound = False
				for key, voiceName in voices.items():
					if settings["command"].lower() + key == data.GetParam(0).lower():
						voice = voiceName
						voiceFound = True
						break

				# if voice hasnt been found
				if not voiceFound:
					SendMessage(settings["responseUserLanguageNotFound"])
					return

				users[data.User] = ConvertDatetimeToEpoch() # set last usage to "now"
				Parent.RemovePoints(data.User, settings["userPointsCost"])
				tts["queue"].append({
					"user": data.User,
					"voice": voice.replace(" ", "\%20"),
					"message": " ".join(data.Message.split(" ")[1:]).replace(" ", "\%20"),
				})
	return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	global tts, settings, voices

	t1 = time.time()
	if tts["timeUntilReady"] < 0:
		if len(tts["queue"]) > 0:
			current = tts["queue"].pop(0)
			if len(current["message"]) != "":
				Parent.GetRequest("https://warp.world/scripts/tts-message?streamer={0}&key={1}&viewer={2}&bar={3}&font={4}&sfont={5}&bfont={6}&gfont={7}&voice={8}&vol={9}&alert=false&message={10}".format(\
					Parent.GetChannelName(), settings["randomKey"], current["user"], settings["messageColor"], settings["fontColor"], settings["fontSize"], settings["fontOutlineColor"],\
					settings["googleFont"], current["voice"], str(settings["volume"]), cgi.escape(current["message"])), {})
			tts["timeUntilReady"] = len(current["message"]) / 8

	else:
		tts["timeUntilReady"] -= t1 - tts["timeOfLastTick"]
	tts["timeOfLastTick"] = t1
	return

#---------------------------------------
#	Buttons on the UI
#---------------------------------------

def ClearQueue():
	global tts
	tts["queue"] = []
	tts["timeUntilReady"] = 0

#---------------------------------------
#	Helper Functinos
#---------------------------------------

def ConvertDatetimeToEpoch(datetimeObject=datetime.datetime.now()):
	# converts a datetime object to seconds in python 2.7
	return time.mktime(datetimeObject.timetuple())

def AddSecondsToDatetime(datetimeObject, seconds):
	# returns a new datetime object by adding x seconds to a datetime object
	return datetimeObject + datetime.timedelta(seconds=seconds)

def ConvertEpochToDatetime(seconds=0):
	# 0 seconds as input would return 1970, 1, 1, 1, 0
	seconds = max(0, seconds)
	return datetime.datetime.fromtimestamp(seconds)

def SendMessage(string):
	global responseVariables
	for variable, text in responseVariables.items():
		if type(text) == type(0.1):
			string = string.replace(variable, str(int(text)))
		else:
			string = string.replace(variable, str(text))
	Parent.SendTwitchMessage(string[:490])


