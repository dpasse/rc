import math
import random
from typing import List, Tuple, TypeVar, Optional
from enum import Enum
from abc import ABC, abstractmethod


# pylint: disable=C0103
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
# pylint: enable=C0103

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

# pylint: disable=C0103
TEventVariableHierarchy = TypeVar('TEventVariableHierarchy', bound='EventVariableHierarchy')
# pylint: enable=C0103

class EventVariableHierarchy(EventVariable):
    def __init__(self: TEventVariableHierarchy,
                 key: str,
                 event_code: EventCodes=EventCodes.ParentEvent,
                 probability: float = 1,
                 children: Optional[List[TEventVariableHierarchy]] = None
        ):
        super().__init__(event_code, probability)

        self.__key = key
        self.__children = children if children else []

    @property
    def key(self: TEventVariableHierarchy) -> str:
        return self.__key

    @property
    def children(self: TEventVariableHierarchy) -> List[TEventVariableHierarchy]:
        return self.__children

    def __repr__(self: TEventVariableHierarchy) -> str:
        return f'<EventVariableHierarchy key="{self.key}" ' + \
            f'probability="{self.probability}", ' + \
            f'children="{len(self.children)}">'

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
    def __init__(self, key: str, data: dict, likelihood_keys: List[str]) -> None:
        self.__key = key
        self.__data = data.copy()
        self.__likelihood_keys = likelihood_keys.copy()

    @property
    def key(self) -> str:
        return self.__key

    def likelihoods(self) -> dict:
        likelihood = {}
        for key in self.__likelihood_keys:
            likelihood[key] = self.__data[key] / self.__data['PA']

        return likelihood

class PitcherStats(PlayerStats):
    def __init__(self, key: str, data: dict):
        super().__init__(key, data, [])

class BatterStats(PlayerStats):
    def __init__(self, key: str, data: dict, probability_of_hitting: float = 1):
        given_data = data.copy()

        assert 'PA' in given_data or 'AB' in given_data
        for column in ('SH', 'SF', 'K', 'BB', 'HBP', '1B', '2B', '3B', 'HR'):
            assert column in given_data

        if not 'PA' in given_data:
            given_data['PA'] = sum(
                given_data[column] for column in ('BB', 'HBP', 'AB', 'SH', 'SF')
            )

        given_data['HITS'] = sum(
            given_data[column] for column in ('1B', '2B', '3B', 'HR')
        )

        given_data['E'] = math.floor(.018 * given_data['PA'])
        given_data['AtBats'] = sum(
            given_data[column] for column in ('AB', 'SF', 'SH')
        )
        given_data['Outs'] = given_data['AtBats'] - \
            sum(given_data[column] for column in ('HITS', 'E', 'K'))

        super().__init__(key, given_data, [
            'E',
            'Outs',
            'K',
            'BB',
            'HBP',
            '1B',
            '2B',
            '3B',
            'HR'
        ])

        self.__probability = probability_of_hitting

    @property
    def probability(self) -> float:
        return self.__probability

T = TypeVar('T', EventVariable, BatterStats)
def create_probability_ranges(events: List[T]) -> List[Tuple[float, T]]:
    threshold = 0.0
    ranges: List[Tuple[float, T]] = []
    for i, event in enumerate(events):
        threshold = 1 if len(events) - 1 == i else threshold + event.probability
        ranges.append((threshold, event))

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
        event_variables: List[EventVariable] = []
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
    def next(self) -> Tuple[BatterStats, List[EventVariable]]:
        pass

class Batters(AbstractBatters):
    def __init__(self, players: List[BatterStats], event_variable_factory = EventVariableFactory()):
        self.__players = players
        self.__ranges = create_probability_ranges(players)
        self.__lookup = {
            i: event_variable_factory.create_with_ranges(player.likelihoods()) for i,  player in enumerate(players)
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
    def __init__(self, players: List[BatterStats], event_variable_factory = EventVariableFactory()):
        self.__at_bat = 0
        self.__players = players
        self.__lookup = {
            i: event_variable_factory.create_with_ranges(player.likelihoods()) for i,  player in enumerate(players)
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
