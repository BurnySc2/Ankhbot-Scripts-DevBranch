import time

Parent = None  # type: ParentClass


class Bet(object):
    def __init__(self):
        # TODO: Add script settings as argument, e.g. min bet amount, max bet amount, win command, lose command, allow multiple entries
        self.min_bet_amount = 0
        self.max_bet_amount = 100
        self.command_win = "win"
        self.command_lose = "lose"

        self.allow_multiple_entries = False

        self.gamblers = set()
        self.bets = []

        self.total_gambled = 0
        self.total_gambled_win = 0
        self.total_gambled_lose = 0
        self.time_since_last_joined = time.time()

    def gambler_allowed_to_join(self, user_id, investment_amount):
        if Parent.GetPoints(user_id) < investment_amount:
            return False
        if user_id in self.gamblers and not self.allow_multiple_entries:
            return False
        if (
            investment_amount < self.min_bet_amount
            or self.max_bet_amount < investment_amount
        ):
            return False
        return True

    def add_gambler(self, user_id, investment_amount, bet_choice, ignore_check=True):
        if ignore_check or self.gambler_allowed_to_join(user_id, investment_amount):
            self.gamblers.add(user_id)
            self.bets.append([user_id, investment_amount, bet_choice])
            Parent.RemovePoints(user_id)
            return True
        return False
