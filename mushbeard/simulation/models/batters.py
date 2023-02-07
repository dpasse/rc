import random
from typing import List, Tuple
from abc import ABC, abstractmethod

from .event_variable import EventVariable
from .stats import BatterStats
from .helpers import create_probability_ranges
from .event_variable_hierarchy import BatterEventVariableFactory


class AbstractBatters(ABC):
    @abstractmethod
    def next(self) -> Tuple[BatterStats, List[EventVariable]]:
        pass

class Batters(AbstractBatters):
    def __init__(self, players: List[BatterStats], event_variable_factory = BatterEventVariableFactory()):
        self.__players = players
        self.__ranges = create_probability_ranges(players)
        self.__lookup = {
            i: event_variable_factory.create_with_ranges(player) for i,  player in enumerate(players)
        }

    def next(self) -> Tuple[BatterStats, List[EventVariable]]:
        if len(self.__ranges) == 1:
            return (self.__players[0], self.__lookup[0])

        rand = random.random()
        for i, probability_range in enumerate(self.__ranges):
            if rand <= probability_range[0]:
                return (self.__players[i], self.__lookup[i])

        raise ValueError('No player was found.')

class BattersWithBattingOrder(AbstractBatters):
    def __init__(self, players: List[BatterStats], event_variable_factory = BatterEventVariableFactory()):
        self.__at_bat = 0
        self.__players = players
        self.__lookup = {
            i: event_variable_factory.create_with_ranges(player) for i,  player in enumerate(players)
        }

    def next(self) -> Tuple[BatterStats, List[EventVariable]]:
        ## at bat
        i = self.__at_bat

        ## setup next batter
        self.__at_bat += 1
        if not self.__at_bat in self.__lookup.keys():
            ## top of the order
            self.__at_bat = 0

        return (self.__players[i], self.__lookup[i])

class BattersFactory():
    def create_batters(self, players_with_probs: List[Tuple[str, dict, float]]) -> Batters:
        return Batters([
            BatterStats(key, player, probability)
            for key, player, probability
            in players_with_probs
        ])

    def create_batters_with_batting_order(self, players_with_probs: List[Tuple[str, dict, float]]) -> BattersWithBattingOrder:
        return BattersWithBattingOrder([
            BatterStats(key, player, probability)
            for key, player, probability
            in players_with_probs
        ])
