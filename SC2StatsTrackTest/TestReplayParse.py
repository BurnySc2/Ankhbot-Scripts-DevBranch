
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
for player in replay.players:
    # toon_id == 0 if that player is a computer
    if player.toon_id == int(playerName.split("-")[-1]):
        streamer = player
        break

# if streamer is in this replay: print result and avg apm
if streamer:
    print("Streamer's result of this replay is: " + str(streamer.result))
    print(streamer.avg_apm)
else:
    print("Streamer has not been found in this replay.")

print(2 / 0)

"""
wichtige sachen kappa:
- spielernamen
- rassen
- win loss
- map name
- server (eu / na)
- avg apm
- avg unspent resources
- game duration
- toon ID
- game type: custom / unranked / ranked
- - replay.is_ladder
- - replay.is_private
- - replay.game_type
- game mode: 1v1 or 2v2
- date played
- which season played in
- hero unit
- supply blocked time
[- constant scv production]
- league (e.g. master vs diamond)

- streaming session (date / time)


"""
