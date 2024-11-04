import pandas as pd

from data.kbo.naver import NaverGame, SingleInning

from datetime import datetime
from enum import Enum


class KBOTeamStatiz(Enum):
    SAMSUNG_LIONS = 1001
    KIA_TIGERS = 2002
    LOTTE_GIANTS = 3001
    LG_TWINS = 5002
    DOOSAN_BEARS = 6002
    HANHWA_EAGLES = 7002
    SSG_LANDERS = 9002
    KIWOOM_HEROS = 10001
    NC_DINOS = 11001
    KT_WIZS = 12001


class KBOTeamNaver(Enum):
    SAMSUNG_LIONS = "SS"
    KIA_TIGERS = "HT"
    LOTTE_GIANTS = "LT"
    LG_TWINS = "LG"
    DOOSAN_BEARS = ""
    HANHWA_EAGLES = ""
    SSG_LANDERS = ""
    KIWOOM_HEROS = ""
    NC_DINOS = ""
    KT_WIZS = ""


class KBOSchedule:
    def __init__(self) -> None:
        
        pass