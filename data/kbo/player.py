from kbo.statiz import request_team_members
from kbo.naver import NaverPlayerId

import pandas as pd


class PlayerId:
    def __init__(self, team: str):
        self.team = team

    def team_member_id(self, year: int):
        # Statiz's Player ID
        statiz_id = request_team_members(self.team, year)

        # Naver's Player ID
        naver_id = NaverPlayerId(self.team, self.team, year)
        naver_id = naver_id.request_player_id()

        player_id = pd.merge(statiz_id, naver_id, on='player_name', how='left')
        return player_id
