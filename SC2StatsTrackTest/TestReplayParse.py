
# https://github.com/ggtracker/sc2reader
import sc2reader
#import s2protocol
import os
import glob

from sc2reader.engine.plugins import APMTracker

sc2reader.engine.register_plugin(APMTracker())

bnetId = "111732023"
playerName = "2-S2-1-727565"
usernames = "BuRny"


replayPath = os.path.join(os.path.expanduser(
    "~"), r"Documents\StarCraft II\Accounts\%s\%s\Replays\Multiplayer" % (bnetId, playerName))

replays = [os.path.join(replayPath, x) for x in os.listdir(
    replayPath) if x.endswith('.SC2Replay')]

replayFile = max(replays, key=os.path.getmtime)

# for testing purposes:
path = os.path.dirname(__file__)
replayFile = os.path.join(path, "Odyssey.SC2Replay")


replay = sc2reader.load_replay(replayFile, load_map=False)

# find streamer in the replay
for x in replay.players:
    # toon_id == 0 if that player is a computer
    if x.toon_id == int(playerName.split("-")[-1]):
        player = x
        break

# if streamer is in this replay: print result and avg apm
if player:
    print("Streamer's result of this replay is: " + str(player.result))
    print(player.avg_apm)
else:
    print("Streamer has not been found in this replay.")
