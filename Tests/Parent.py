class ParentClass(object):
    def __init__(self, channel="burnysc2", currency="Bugs"):
        self.info = {"channel": channel, "currency": currency}

    def GetChannelName(self):
        return self.info["channel"]

    def GetCurrencyName(self):
        return self.info["currency"]

    def GetDisplayName(self, user):
        print("Returning display name for user {}".format(user))
        return user

    def GetPoints(self, user):
        print("Returning points for user {}".format(user))
        return 1500

    def HasPermission(self, user, role="Moderator", idk=""):
        return True

    def BroadcastWsEvent(self, even_name, json):
        return

    def AddPoints(self, user, username, amount):
        print(
            "Adding points for user {} with username {}, amount: {}".format(
                user, username, amount
            )
        )
        return

    def RemovePoints(self, user, username, amount):
        print(
            "Removing points for user {} with username {}, amount: {}".format(
                user, username, amount
            )
        )
        return

    def SendStreamMessage(self, message):
        print("Sending message to stream: {}".format(message))
        return

    def GetRequest(self, url, json):
        print("Get request to URL: {}".format(url))
        return [{}]
