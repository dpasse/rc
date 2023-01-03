import math
from typing import List
from enum import Enum


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
    def __init__(self, key: str, probability: float, event_code: EventCodes):
        self.key = key
        self.probability = probability
        self.event_code = event_code

    def __repr__(self):
        return f'<EventVariables {self.key} - {self.probability}%>'

class EventVariableHierarchy(EventVariable):
    def __init__(self, key: str, probability: float, event_code: EventCodes=None, children: list = []):
        self.key = key
        self.probability = probability
        self.event_code = event_code
        self.children = children

    def __repr__(self):
        return f'<EventVariables {self.key} - {self.probability}%, C={len(self.children)}>'

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

class EventVariableFactory():
    def __init__(self, hierarchy_factory = EventVariableHierarchyFactory()):
        self.hierarchy_factory = hierarchy_factory

    def create(self, likelihoods: dict) -> list:
        return self.flatten_hierarchy(
            self.hierarchy_factory.create(likelihoods).children
        )

    def flatten_hierarchy(self, event_variable_hierarchy: List[EventVariableHierarchy], parent_probability: float = 1) -> list:
        event_variables = []
        for event_variable in event_variable_hierarchy:
            key = event_variable.key
            probability = event_variable.probability
            event_code = event_variable.event_code

            if event_code is None:
                event_variables.extend(
                    self.flatten_hierarchy(event_variable.children, parent_probability * probability)
                )
            else:
                event_variables.append(
                    EventVariable(key, parent_probability * probability, event_code)
                )

        return event_variables

class PlayerStats():
    def __init__(self, data):
        self.data = data.copy()

        for key in ['SH', 'SF', 'K', 'BB', 'HBP', '1B', '2B', '3B', 'HR']:
            assert key in self.data

        assert 'PA' in self.data or 'AB' in self.data

        self.data['HITS'] = sum([ self.data[key] for key in ['1B', '2B', '3B', 'HR']])

        if not 'PA' in self.data:
            self.data['PA'] = sum([ self.data[key] for key in ['BB', 'HBP', 'AB', 'SH', 'SF']])

        self.data['E'] = math.floor(.018 * self.data['PA'])
        self.data['AtBats'] = sum([ self.data[key] for key in ['AB', 'SF', 'SH']])
        self.data['Outs'] = self.data['AtBats'] - sum([ self.data[key] for key in ['HITS', 'E', 'K']])

    def likelihoods(self):
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
            lh[key] = self.data[key] / self.data['PA']

        return lh
