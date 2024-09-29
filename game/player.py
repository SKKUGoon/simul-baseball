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


class Batter(Player):
    def __init__(self):
        super().__init__()


class Team:
    def __init__(self) -> None:
        self.batter_line: List[Batter] = list()
        self.pitcher_line: List[Pitcher] = list()
        pass

    