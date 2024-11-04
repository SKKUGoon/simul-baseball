from game.player import Team, Batter, Pitcher
from typing import Literal, Dict
import random


class Game:
    def __init__(self, home: Team, away: Team):
        # Teams + Members
        self.home = home
        self.away = away

        # Offense
        self.offense: Literal["home", "away"] = "home"
        self.defense: Literal["home", "away"] = "away"

        # Bases
        self.base1: Batter | None = None
        self.base2: Batter | None = None
        self.base3: Batter | None = None
        self.out_count = 0
        self.strike = 0
        self.ball = 0

        self.curr_inning = 1
        
        # Scores
        self.home_score = 0
        self.away_score = 0

    def switch_offensive(self):
        if self.offense == "home" and self.defense == "away":
            self.offense == "away"
            self.defense == "home"
        elif self.offense == "away" and self.defense == "home":
            self.offense = "home"
            self.defense = "away"
        else:
            raise RuntimeError("[GameErr]: Offensive-Defensive mismatch")

    def start_inning(self):
        # Initialize inning
        self.base1 = None
        self.base2 = None
        self.base3 = None
        self.out_count = 0
        self.strike = 0
        self.ball = 0

    def play_inning(self):
        offensive: Team = getattr(self, self.offense)
        defensive: Team = getattr(self, self.defense)

        # Defensive
        pitcher = defensive.pitcher_line[defensive.pitcher_index]

        while self.out_count < 3:
            # Offensive
            batter = offensive.batter_line[offensive.batting_index]

            # Calculate probabilities
            outcome = self.vs_prediction(pitcher, batter)

            # Simulate the at-bat. Process the result
            move_to_next_batter = self.at_bat(outcome)

            if move_to_next_batter:
                offensive.batting_index += 1 % len(offensive.batter_line)
        
        self.switch_offensive()
        self.start_inning()

    def vs_prediction(self, pitcher, batter):
        # TODO: Not implemented
        pitch = ...  # Generate pitch info from the pitch distribution
        batter_info = ...  # Retrieve batter's stat from the database
        feature = generate_feature(pitch, batter_info)

        model = ...  # Load model
        outcome = model.fit(feature)

        return outcome
    
    def at_bat(self, outcome):
        if outcome == "B":
            return False
        elif outcome == "HO":
            return True
        ...