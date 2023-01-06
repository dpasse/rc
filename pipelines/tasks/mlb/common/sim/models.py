import math
import random
from typing import List, Tuple, TypeVar
from enum import Enum
from abc import ABC, abstractmethod


class EventCodes(Enum):
    Strikeout = 1
    Walk = 2
    HBP = 3
    Error = 4
    LongSingle = 5
    MediumSingle = 6
    ShortSingle = 7
    ShortDouble = 8
    LongDouble = 9
    Triple = 10
    HR = 11
    GIDP = 12
    NormalGroundBall = 13
    NoAdvanceGroundBall = 14
    LineDriveInfieldFly = 15
    LongFly = 16
    MediumFly = 17
    ShortFly = 18
    ParentEvent = 100

all_event_codes = [
    EventCodes.Strikeout,
    EventCodes.Walk,
    EventCodes.HBP,
    EventCodes.Error,
    EventCodes.LongSingle,
    EventCodes.MediumSingle,
    EventCodes.ShortSingle,
    EventCodes.ShortDouble,
    EventCodes.LongDouble,
    EventCodes.Triple,
    EventCodes.HR,
    EventCodes.GIDP,
    EventCodes.NormalGroundBall,
    EventCodes.NoAdvanceGroundBall,
    EventCodes.LineDriveInfieldFly,
    EventCodes.LongFly,
    EventCodes.MediumFly,
    EventCodes.ShortFly,
]

class EventVariable():
    def __init__(self, event_code: EventCodes = EventCodes.ParentEvent, probability: float = 1):
        self.__event_code = event_code
        self.__probability = probability

    @property
    def event_code(self) -> EventCodes:
        return self.__event_code

    @property
    def probability(self) -> float:
        return self.__probability

    def __repr__(self):
        event_name = 'EMPTY' if self.event_code is None else self.event_code.name
        return f'<EventVariable name="{event_name}" probability="{self.probability}">'

class EventVariableHierarchy(EventVariable):
    def __init__(self, key: str, event_code: EventCodes=EventCodes.ParentEvent, probability: float = 1, children: list = []):
        super().__init__(event_code, probability)

        self.__key = key
        self.children = children

    @property
    def key(self) -> str:
        return self.__key

    def __repr__(self):
        return f'<EventVariableHierarchy key="{self.key}" probability="{self.probability}", children="{len(self.children)}">'

class EventVariableHierarchyFactory():
    def create(self, likelihoods: dict) -> EventVariableHierarchy:
        return EventVariableHierarchy(
            key='Mathletics',
            probability=1,
            children=[
                EventVariableHierarchy(
                    key='Error',
                    probability=likelihoods['E'],
                    event_code=EventCodes.Error
                ),
                EventVariableHierarchy(
                    key='Outs',
                    probability=likelihoods['Outs'],
                    children=[
                        ## Grounders
                        EventVariableHierarchy(
                            key='Ground Out',
                            probability=.538,
                            children=[
                                EventVariableHierarchy(
                                    key='Double Play',
                                    probability=.5,
                                    event_code=EventCodes.GIDP
                                ),
                                EventVariableHierarchy(
                                    key='Normal Ground Out',
                                    probability=.5,
                                    event_code=EventCodes.NormalGroundBall
                                )
                            ]
                        ),
                        ## Infield
                        EventVariableHierarchy(
                            key='Infield Fly / Line Drive',
                            probability=.153,
                            event_code=EventCodes.LineDriveInfieldFly
                        ),
                        ## Fly
                        EventVariableHierarchy(
                            key='Fly Out',
                            probability=.309,
                            children=[
                                EventVariableHierarchy(
                                    key='Long Fly Out',
                                    probability=.2,
                                    event_code=EventCodes.LongFly
                                ),
                                EventVariableHierarchy(
                                    key='Medium Fly Out',
                                    probability=.5,
                                    event_code=EventCodes.MediumFly
                                ),
                                EventVariableHierarchy(
                                    key='Short Fly Out',
                                    probability=.3,
                                    event_code=EventCodes.ShortFly
                                )
                            ]
                        )
                    ]
                ),
                EventVariableHierarchy(
                    key='K',
                    probability=likelihoods['K'],
                    event_code=EventCodes.Strikeout
                ),
                EventVariableHierarchy(
                    key='BB',
                    probability=likelihoods['BB'],
                    event_code=EventCodes.Walk
                ),
                EventVariableHierarchy(
                    key='HBP',
                    probability=likelihoods['HBP'],
                    event_code=EventCodes.HBP
                ),
                EventVariableHierarchy(
                    key='1B',
                    probability=likelihoods['1B'],
                    children=[
                        ## Long
                        EventVariableHierarchy(
                            key='Long 1B',
                            probability=.3,
                            event_code=EventCodes.LongSingle
                        ),
                        ## Medium
                        EventVariableHierarchy(
                            key='Medium 1B',
                            probability=.5,
                            event_code=EventCodes.MediumSingle
                        ),
                        ## Short
                        EventVariableHierarchy(
                            key='Short 1B',
                            probability=.2,
                            event_code=EventCodes.ShortSingle
                        )
                    ]
                ),
                EventVariableHierarchy(
                    key='2B',
                    probability=likelihoods['2B'],
                    children=[
                        ## Short
                        EventVariableHierarchy(
                            key='Short 2B',
                            probability=.8,
                            event_code=EventCodes.ShortDouble
                        ),
                        ## Long
                        EventVariableHierarchy(
                            key='Long 2B',
                            probability=.2,
                            event_code=EventCodes.LongDouble
                        ),
                    ]
                ),
                EventVariableHierarchy(
                    key='3B',
                    probability=likelihoods['3B'],
                    event_code=EventCodes.Triple
                ),
                EventVariableHierarchy(
                    key='HR',
                    probability=likelihoods['HR'],
                    event_code=EventCodes.HR
                ),
            ]
        )

class PlayerStats():
    def __init__(self, key: str, data: dict, probability_of_hitting: float = 1):
        self.__key  = key
        self.__data = data.copy()

        for key in ['SH', 'SF', 'K', 'BB', 'HBP', '1B', '2B', '3B', 'HR']:
            assert key in self.__data

        assert 'PA' in self.__data or 'AB' in self.__data

        self.__data['HITS'] = sum([ self.__data[key] for key in ['1B', '2B', '3B', 'HR']])

        if not 'PA' in self.__data:
            self.__data['PA'] = sum([ self.__data[key] for key in ['BB', 'HBP', 'AB', 'SH', 'SF']])

        self.__data['E'] = math.floor(.018 * self.__data['PA'])
        self.__data['AtBats'] = sum([ self.__data[key] for key in ['AB', 'SF', 'SH']])
        self.__data['Outs'] = self.__data['AtBats'] - sum([ self.__data[key] for key in ['HITS', 'E', 'K']])

        self.__probability = probability_of_hitting

    @property
    def key(self) -> str:
        return self.__key

    @property
    def probability(self) -> float:
        return self.__probability

    def likelihoods(self) -> dict:
        keys = [
            'E',
            'Outs',
            'K',
            'BB',
            'HBP',
            '1B',
            '2B',
            '3B',
            'HR'
        ]

        lh = {}
        for key in keys:
            lh[key] = self.__data[key] / self.__data['PA']

        return lh

T = TypeVar('T', EventVariable, PlayerStats)
def create_probability_ranges(events: List[T]) -> List[Tuple[float, T]]:
    threshold = 0.0
    ranges: List[Tuple[float, T]] = []
    for i, ev in enumerate(events):
        threshold = 1 if len(events) - 1 == i else threshold + ev.probability
        ranges.append((threshold, ev))

    return ranges

class EventVariableFactory():
    def __init__(self, hierarchy_factory = EventVariableHierarchyFactory()):
        self.__hierarchy_factory = hierarchy_factory

    def create(self, likelihoods: dict) -> List[EventVariable]:
        return self.flatten_hierarchy(
            self.__hierarchy_factory.create(likelihoods).children
        )

    def create_with_ranges(self, likelihoods: dict) -> List[Tuple[float, EventVariable]]:
        events = self.create(likelihoods)
        return create_probability_ranges(events)

    def flatten_hierarchy(self, event_variable_hierarchy: List[EventVariableHierarchy], parent_probability: float = 1) -> List[EventVariable]:
        event_variables = []
        for event_variable in event_variable_hierarchy:
            probability = event_variable.probability
            event_code = event_variable.event_code

            if event_code == EventCodes.ParentEvent:
                event_variables.extend(
                    self.flatten_hierarchy(event_variable.children, parent_probability * probability)
                )
            else:
                event_variables.append(
                    EventVariable(event_code, parent_probability * probability)
                )

        return event_variables

class AbstractBatters(ABC):
    @abstractmethod
    def next(self) -> Tuple[PlayerStats, List[EventVariable]]:
        pass

class Batters(AbstractBatters):
    def __init__(self, players: List[PlayerStats], event_variable_factory = EventVariableFactory()):
        self.__players = players
        self.__ranges = create_probability_ranges(players)
        self.__lookup = {
            i: event_variable_factory.create_with_ranges(player.likelihoods()) for i,  player in enumerate(players)
        }

    def next(self) -> Tuple[PlayerStats, List[EventVariable]]:
        if len(self.__ranges) == 1:
            return (self.__players[0], self.__lookup[0])

        rv = random.random()
        for i, range in enumerate(self.__ranges):
            p, _ = range
            if rv <= p:
                return (self.__players[i], self.__lookup[i])


        raise ValueError('No player was found.')

class BattersWithBattingOrder(AbstractBatters):
    def __init__(self, players: List[PlayerStats], event_variable_factory = EventVariableFactory()):
        self.__at_bat = 0
        self.__players = players
        self.__lookup = {
            i: event_variable_factory.create_with_ranges(player.likelihoods()) for i,  player in enumerate(players)
        }

    def next(self) -> Tuple[PlayerStats, List[EventVariable]]:
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
            PlayerStats(key, player, probability)
            for key, player, probability
            in players_with_probs
        ])

    def create_batters_with_batting_order(self, players_with_probs: List[Tuple[str, dict, float]]) -> BattersWithBattingOrder:
        return BattersWithBattingOrder([
            PlayerStats(key, player, probability)
            for key, player, probability
            in players_with_probs
        ])
