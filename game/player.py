from enum import Enum
from typing import List


class PlayerStat:
    def __init__(self):
        pass

    @classmethod
    def from_dict(cls, stat_config):
        return PlayerStat()
    
    @classmethod
    def from_database(cls, db):
        return PlayerStat()


class AtBat:
    def __init__(self, player):
        ...

    def at_bat(self):
        ...


class Player:
    def __init__(self):
        pass

    def __repr__(self) -> str:
        pass

    def insert_stats(self, stats: PlayerStat):
        ...
    ...


class Pitcher(Player):
    def __init__(self):
        super().__init__()
        self.stats = dict()  # TODO: Placeholder


class Batter(Player):
    def __init__(self):
        super().__init__()
        self.stats = dict()  # TODO: Placeholder


class Team:
    def __init__(self, batter_line: List[Batter], pitcher_line: List[Pitcher]) -> None:
        self.batter_line: List[Batter] = batter_line
        self.pitcher_line: List[Pitcher] = pitcher_line  # Starting pitcher + Reserves

        self.pitcher_index: int = 0
        self.batting_index: int = 0
        pass

    def next_pitcher(self):
        self.pitcher_index += 1

    def next_batter(self):
        self.batting_index += 1
    

    