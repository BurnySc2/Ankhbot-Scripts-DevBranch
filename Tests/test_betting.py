import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
try:
    from .Data import DataClass
    from .Parent import ParentClass
except:
    from Data import DataClass
    from Parent import ParentClass

from .SC2BetSystem.betting import Bet

# import sys
# sys.path.append("..")

Parent = ParentClass()


def test_betting_object():
    bet = Bet()
    assert bet.gambler_allowed_to_join("burny", 50)
    assert bet.add_gambler("burny", 50)
    assert not bet.gambler_allowed_to_join("burny", 50)
