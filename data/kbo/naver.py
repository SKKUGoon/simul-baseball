# Naver Text Relays Crawling
import requests
import pandas as pd

from typing import Dict
from enum import Enum
from datetime import datetime
from uuid import uuid4


KBO_NAVER_LOGS_URL = "https://api-gw.sports.naver.com/schedule/games"


def generate_game_id(home_team, away_team, date: datetime) -> str:
    return f"{date.strftime('%Y%m%d')}{home_team}{away_team}0{date.year}"


def request_game_logs(home_team, away_team, date: datetime, inning: int):
    header = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "authority": "api-gw.sports.naver.com",
        "Origin": "https://m.sports.naver.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    gid = generate_game_id(home_team, away_team, date)
    url = f"{KBO_NAVER_LOGS_URL}/{gid}/relay"

    param = {'inning': inning}
    resp = requests.get(url, params=param, headers=header)

    if resp.status_code == 200:
        jstr = resp.json()
        
        try:
            game_logs = jstr['result']['textRelayData']['textRelays']
            return game_logs
        except KeyError:
            RuntimeError("no key named ('result', 'textRelayData')")
    else:
        RuntimeError(resp.status_code)


class NaverGameLogParser:
    def __init__(self, data: Dict):
        if 'titleStyle' not in data.keys() or data['titleStyle'] != '8':
            raise KeyError("not a correct log style")
        
        self.data = data
        self.vs_id = str(uuid4())

    @property
    def curr_inning(self) -> int:
        return self.data['inn']
    
    @property
    def home_or_away(self) -> str:
        if self.data['homeOrAway'] == '0':
            return 'away'
        elif self.data['homeOrAway'] == '1':
            return 'home'

    def vs_log(self) -> pd.DataFrame:
        logs = self.data['textOptions']
        pitches = [l for l in logs if l['type'] == 1]

        vs, ball = list(), list()
        ball_col, vs_col = None, None
        for pitch_info, pts in zip(pitches, self.data['ptsOptions']):
            p = PitchResult(pitch_info)
            p = [
                p.id, 
                self.vs_id, 
                int(p.pitch_num), 
                p.pitch_type, 
                float(p.pitch_speed), 
                p.pitch_result, 
                *list(pitch_info['currentGameState'].values())
            ]
            
            vs.append(p)
            ball.append(list(pts.values()))  # Topology of pitches

            if vs_col is None:
                vs_col = list(pitch_info['currentGameState'].keys())

            if ball_col is None:
                ball_col = list(pts.keys())

        vs = pd.DataFrame(vs, columns=["pitchId", "resultId", "ballCount", "type", "speed", "result", *vs_col])
        ball = pd.DataFrame(ball, columns=ball_col)
        ball.columns = ["pitchId", "inn", "ballCount", *ball.columns[3:]]
        
        return pd.merge(vs, ball, on=['pitchId', 'ballCount'], how='left')
    
    def vs_result(self) -> pd.DataFrame:
        logs = self.data['textOptions']
        res, oth = ([l for l in logs if l['type'] == 13],  # Batter's result
                    [l for l in logs if l['type'] == 14])  # Other base runner's result
        
        # `currentGameState` shows the resulting effect 
        # `text` to understand the content

        assert len(res) == 1  # Should only have one result
        res = res[0]  
        res_data = [[res['text'], self.vs_id, *list(res['currentGameState'].values())]]

        oth_data = list()
        for o in oth:
            oth_data.append(
                [o['text'], self.vs_id, *list(o['currentGameState'].values())]
            )

        data = pd.DataFrame(res_data + oth_data, columns=["text", "resultId", *list(res['currentGameState'].keys())])
        return data
        
        
class PitchResult:
    def __init__(self, vs: Dict):
        # vs: log's textOption. type is 1
        self.pitch = vs

    @property
    def pitch_num(self):
        return self.pitch['pitchNum']
    
    @property
    def pitch_result(self):
        # S: 헛스윙
        # H: 히트, Fly Out Included
        # T: Strike
        # B: Ball
        # F: Foul
        return self.pitch['pitchResult']  # Swing (Swing & Miss)
    
    @property
    def pitch_speed(self):
        return self.pitch['speed']
    
    @property
    def pitch_type(self):
        return self.pitch['stuff']
    
    @property
    def id(self):
        return self.pitch['ptsPitchId']
