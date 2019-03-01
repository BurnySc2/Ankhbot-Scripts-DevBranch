class DataClass(object):
    def __init__(self, user="burnysc2", username="BurnySc2", message="Hello world"):
        self.info = {"user": user, "username": username, "message": message}

    @property
    def User(self):
        return self.info["user"]

    @property
    def UserName(self):
        return self.info["username"]

    @property
    def Message(self):
        return self.info["message"]

    @property
    def RawData(self):
        return ""

    @property
    def ServiceType(self):
        return ""

    def IsChatMessage(self):
        return True

    def IsRawData(self):
        return True

    def IsFromTwitch(self):
        return True

    def IsFromYoutube(self):
        return False

    def IsFromMixer(self):
        return False

    def IsFromDiscord(self):
        return False

    def IsWhisper(self):
        return False

    def GetParam(self, value):
        return self.Message.strip().split(" ")[value]

    def GetParamCount(self, value):
        return len(self.Message.strip().split(" "))
