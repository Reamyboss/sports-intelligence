from enum import Enum


class PredictionMarket(str, Enum):
    MATCH_WINNER = "MATCH_WINNER"

    DOUBLE_CHANCE = "DOUBLE_CHANCE"

    BOTH_TEAMS_TO_SCORE = "BOTH_TEAMS_TO_SCORE"

    OVER_UNDER = "OVER_UNDER"