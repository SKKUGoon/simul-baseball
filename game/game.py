from game.player import Team, Batter, Pitcher
from typing import Literal, Dict
import random


# League average rates
league_avg_rates = {
    'SO': 0.22,
    'BB': 0.08,
    'HBP': 0.01,
    'HR': 0.03,
    'double': 0.05,
    'triple': 0.005,
    'single': 0.15,
    'out': 0.455  # Adjusted so that total sums to 1
}


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

    def play_inning(self):
        out_count = 0
        offensive: Team = getattr(self, self.offense)
        defensive: Team = getattr(self, self.defense)

        # Defensive
        pitcher = defensive.pitcher_line[defensive.pitcher_index]

        while out_count < 3:
            # Offensive
            batter = offensive.batter_line[offensive.batting_index]

            # Calculate probabilities
            prob = self.calculate_probability(pitcher, batter)

            # Simulate the at-bat. Process the result
            self.at_bat(prob)

            # Move to next batter
            offensive.batting_index += 1 % len(offensive.batter_line)
        
        self.switch_offensive()
        self.start_inning()

    @staticmethod
    def calculate_probability(p: Pitcher, b: Batter):
        batter = {
            "PA": b["PA"],
            "SO_rate": b["SO"] / b["PA"] if b["PA"] > 0 else 0,
            "BB_rate": b["BB"] / b["PA"] if b["PA"] > 0 else 0,
            "HBP_rate": b["HP"] / b["PA"] if b["PA"] > 0 else 0,
            "HR_rate": b["HR"] / b["PA"] if b["PA"] > 0 else 0,
            "double_rate": b['2B'] / b["PA"] if b["PA"] > 0 else 0,
            "triple_rate": b['3B'] / b["PA"] if b["PA"] > 0 else 0,
            "single_rate": (b["H"] - b["HR"] - b['2B'] - b['3B']) / b["PA"] if b["PA"] > 0 else 0
        }

        pitcher = {
            "TBF": p["TBF"],
            "SO_rate": p["SO"] / p["TBF"] if p["TBF"] > 0 else 0,
            "BB_rate": p["BB"] / p["TBF"] if p["TBF"] > 0 else 0,
            "HBP_rate": p["HP"] / p["TBF"] if p["TBF"] > 0 else 0,
            "HR_rate": p["HR"] / p["TBF"] if p["TBF"] > 0 else 0,
            "double_rate": p["2B"] / p["TBF"] if p["TBF"] > 0 else 0,
            "triple_rate": p["3B"] / p["TBF"] if p["TBF"] > 0 else 0,
            "single_rate": (p["H"] - p["HR"] - p['2B'] - p['3B']) / p["TBF"] if p["TBF"] > 0 else 0
        }

        # Outcomes
        outcomes = ['SO', 'BB', 'HBP', 'HR', 'double', 'triple', 'single', 'out']
        probabilities = {}

        for outcome in outcomes:
            # Batter / Pitcher rate
            batter_rate, pitcher_rate = batter.get(f"{outcome}_rate", 0), pitcher.get(f"{outcome}_rate", 0)

            # League average rate
            league_rate = league_avg_rates[outcome]

            # Batter Factor
            BF = batter_rate / league_rate if league_rate > 0 else 0
            
            # Pitcher Factor
            PF = pitcher_rate / league_rate if league_rate > 0 else 0
            
            # Combined Factor
            if BF > 0 and PF > 0:
                CF = (BF * PF) ** 0.5
            else:
                CF = 0
            
            # Outcome Probability
            OP = league_rate * CF
            
            probabilities[outcome] = OP

        # Normalize probabilities
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            for outcome in probabilities:
                probabilities[outcome] /= total_prob
        else:
            # Assign default probabilities if total_prob is zero
            probabilities = league_avg_rates

        return probabilities

    def advance_runner(self, b: Batter, bases: int):
        ...
        
    def at_bat(self, probability: Dict):
        rand = random.random()
        cumulative = 0
        result = None

        for outcome, probability in probability.items():
            cumulative += probability
            if rand <= 0:
                ...
        ...