# Naver Text Relays Crawling
import requests
import pandas as pd

from typing import Dict, Literal
from datetime import datetime
from uuid import uuid4


KBO_NAVER_LOGS_URL = "https://api-gw.sports.naver.com/schedule/games"


def generate_game_id(home_team, away_team, date: datetime) -> str:
    return f"{date.strftime('%Y%m%d')}{home_team}{away_team}0{date.year}"


class NaverPlayerId:
    def __init__(self, home_team, away_team, date: datetime) -> None:
        self.id = generate_game_id(home_team, away_team, date)

    def request_player_id(self):
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "authority": "api-gw.sports.naver.com",
            "Origin": "https://m.sports.naver.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        url = f"{KBO_NAVER_LOGS_URL}/{self.id}/relay"

        param = {'inning': 1}
        resp = requests.get(url, params=param, headers=header)
        if resp.status_code == 200:
            jstr = resp.json()

            return self.extract_player_id(jstr['result'], "home")  # Always go for home

        else:
            RuntimeError(resp.status_code)

    @staticmethod
    def extract_player_id(data: Dict, home_or_away: Literal["home", "away"]):
        if home_or_away == "home":
            pitcher = [[i[k] for k in ['name', 'pcode']] 
                       for i in data['textRelayData']['homeLineup']['pitcher']]
            batter = [[i[k] for k in ['name', 'pcode']] 
                      for i in data['textRelayData']['homeLineup']['batter']]
            return pd.DataFrame(pitcher + batter, columns=['player_name', 'naver_id'])
        else:
            pitcher = [[i[k] for k in ['name', 'pcode']] 
                       for i in data['textRelayData']['awayLineup']['pitcher']]
            batter = [[i[k] for k in ['name', 'pcode']] 
                      for i in data['textRelayData']['awayLineup']['batter']]
            return pd.DataFrame(pitcher + batter, columns=['player_name', 'naver_id'])



class NaverGame:
    def __init__(self, home_team, away_team, date: datetime) -> None:
        self.id = generate_game_id(home_team, away_team, date)

    def _request_game_logs(self, inning: int):
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "authority": "api-gw.sports.naver.com",
            "Origin": "https://m.sports.naver.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        url = f"{KBO_NAVER_LOGS_URL}/{self.id}/relay"

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

    def data(self):
        total_logs = list()
        for i in range(1, 12+1):  # 12 innings
            game_log = self._request_game_logs(i)
            game_log.reverse()
            total_logs.append(game_log)

        return sum(total_logs, [])
    
    def exec(self):
        # TODO: Insert inning log parser.
        # TODO: Find out which of the 'home' or 'away' starts first
        ...


class NaverGameLogParser:
    def __init__(self, data: Dict):
        if 'titleStyle' not in data.keys() or data['titleStyle'] != '8':
            self.is_trainable = False
        self.is_trainable = True

        self.data = data
        self.vs_id = str(uuid4())

    @property
    def curr_inning(self) -> int:
        return self.data['inn']
    
    @property
    def home_or_away(self) -> Literal["away", "home"]:
        if self.data['homeOrAway'] == '0':
            return 'away'
        elif self.data['homeOrAway'] == '1':
            return 'home'

    # Log TextOption's Type:
    # 1: Batter VS Pitcher Result
    # 7: Illegal activity + ETC Activity
    # 13, 23: Batter himeself
    # 14, 24: Other Result
    def vs_log(self) -> pd.DataFrame | None:
        logs = self.data['textOptions']
        pitches = [l for l in logs if l['type'] == 1]

        if len(pitches) <= 0:
            return None

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
    
    def vs_result(self) -> pd.DataFrame | None:
        logs = self.data['textOptions']
        res, oth = ([l for l in logs if l['type'] == 13 or l['type'] == 23],  # Batter's result
                    [l for l in logs if l['type'] == 14 or l['type'] == 24])  # Other base runner's result
        
        # `currentGameState` shows the resulting effect 
        # `text` to understand the content

        if len(res) < 1:  # Should only have one result
            return None
        
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
    

class BaseOp:
    def __init__(self, base1: str, base2: str, base3: str) -> None:
        self.base1 = base1
        self.base2 = base2
        self.base3 = base3

        self.is_empty_1 = self.base1 == '0'
        self.is_empty_2 = self.base1 == '0'
        self.is_empty_3 = self.base1 == '0'

        self.on_base = {self.base1, self.base2, self.base3}

    def update(self, base1: str, base2: str, base3: str):
        old_base = [self.base1, self.base2, self.base3]
        new_base = [base1, base2, base3]

        batter = [i for i in new_base if i not in old_base and i != ['0']]
        if len(batter) <= 0:
            return "HR"  # All batters went home
        else:
            batter = batter[0]
        
        if new_base.index(batter) == 0:
            return "1H"
        elif new_base.index(batter) == 1:
            return "2H"
        elif new_base.index(batter) == 2:
            return "3H"
        else:
            return "HR"


class SingleInning:
    def __init__(self, 
                 curr_inning: float,
                 home_away: Literal["home", "away"],
                 home_score: int = 0,
                 away_score: int = 0,
                 cumul_home_hits: int = 0,
                 cumul_away_hits: int = 0,
                 cumul_home_bb: int = 0,
                 cumul_away_bb: int = 0,
                 cumul_home_err: int = 0,
                 cumul_away_err: int = 0) -> None:
        
        self.curr_inning = curr_inning
        self.home_away = home_away

        # Inning's status (to be passed to next inning)
        self.home_score: int = home_score
        self.away_score: int = away_score
        self.cumul_home_hits: int = cumul_home_hits
        self.cumul_away_hits: int = cumul_away_hits
        self.cumul_home_bb: int = cumul_home_bb
        self.cumul_away_bb: int = cumul_away_bb
        self.cumul_home_err: int = cumul_home_err
        self.cumul_away_err: int = cumul_away_err

        # Inning's status (this innings only)
        self.outs = 0
        self.base_operation = BaseOp("0", "0", "0")


    def advance_to_next(self):
        ha = None
        if self.home_away == "home":
            ha = "away"
        else:
            ha = "home"

        return SingleInning(
            self.curr_inning + 0.5,
            ha,
            self.home_score,
            self.away_score,
            self.cumul_home_hits,
            self.cumul_away_hits,
            self.cumul_home_bb,
            self.cumul_away_bb,
            self.cumul_home_err,
            self.cumul_away_err,
        )
    
    def insert_log(self, my_log: Dict):
        # Produce trainable dataset from each pitch
        if self.outs == 3:
            print("please advance to next home/away")
            return
        
        # Pitch features        
        feature0_player = ['pitcher', 'batter']
        feature1_columns = [
            'ballCount', 'type', 'speed', 'stance',
            'crossPlateX', 'crossPlateY', 'topSz', 'bottomSz', 
            'vy0', 'vz0', 'vx0', 'z0', 'y0', 'x0', 'ax', 'ay', 'az'
        ]  # Pitch itself
        feature2_columns = ['strike', 'ball', 'out', 'base1', 'base2', 'base3']  # current field features

        # Log parsing
        parser = NaverGameLogParser(my_log)
        if parser.is_trainable is False:
            return None
        
        log, result = parser.vs_log(), parser.vs_result()
        if log is None or result is None:
            return None
        
        feature0s, feature1s, feature2s = list(), list(), list()
        targets = list()
        strike, ball = 0, 0
        for _, log_row in log.iterrows():
            feature0 = pd.DataFrame(log_row).transpose()[feature0_player]
            feature1 = pd.DataFrame(log_row).transpose()[feature1_columns]
            feature2 = pd.DataFrame(
                [
                    [
                        strike, 
                        ball, 
                        self.outs,
                        self.base_operation.base1, 
                        self.base_operation.base2, 
                        self.base_operation.base3
                    ]
                ], 
                columns=feature2_columns
            )
            
            feature0s.append(feature0)
            feature1s.append(feature1)
            feature2s.append(feature2)
            
            target = log_row['result']
            

            if target == 'B':
                ball += 1
            elif target != 'H':
                strike += 1
            else:  # "H" Hit or Out
                if parser.home_or_away == "away":
                    if self.cumul_away_hits != int(result.iloc[-1, :]['awayHit']):
                        target = self.base_operation.update(result.iloc[-1, :]['base1'],
                                                            result.iloc[-1, :]['base2'],
                                                            result.iloc[-1, :]['base3'])
                    else:
                        target = "HO"
                else:
                    if self.cumul_home_hits != int(result.iloc[-1, :]['homeHit']):
                        target = self.base_operation.update(result.iloc[-1, :]['base1'],
                                                            result.iloc[-1, :]['base2'],
                                                            result.iloc[-1, :]['base3'])
                    else:
                        target = "HO"
            
            targets.append([target])

        # Update State
        self.home_score = int(result.iloc[-1, :]['homeScore'])
        self.away_score = int(result.iloc[-1, :]['awayScore'])
        self.cumul_home_hits = int(result.iloc[-1, :]['homeHit'])
        self.cumul_away_hits = int(result.iloc[-1, :]['awayHit'])
        self.cumul_home_bb = int(result.iloc[-1, :]['homeBallFour'])
        self.cumul_away_bb = int(result.iloc[-1, :]['awayBallFour'])
        self.cumul_home_err = int(result.iloc[-1, :]['homeError'])
        self.cumul_away_err = int(result.iloc[-1, :]['awayError'])
        
        self.outs = int(result.iloc[-1, :]['out'])

        self.base_operation.base1 = result.iloc[-1, :]['base1']
        self.base_operation.base2 = result.iloc[-1, :]['base2']
        self.base_operation.base3 = result.iloc[-1, :]['base3']

        # Data
        X = pd.concat([
            pd.concat(feature0s).reset_index(drop=True),
            pd.concat(feature1s).reset_index(drop=True),
            pd.concat(feature2s).reset_index(drop=True),
        ], axis=1)
        y = pd.DataFrame(targets, columns=['target']).reset_index(drop=True)

        return X, y
        


