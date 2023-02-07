from typing import List, TypeVar, Optional, Tuple

from .event_codes import EventCodes
from .event_variable import EventVariable
from .stats import BatterStats
from .helpers import create_probability_ranges


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

class BatterEventVariableHierarchyFactory():
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

class BatterEventVariableFactory():
    def __init__(self, hierarchy_factory = BatterEventVariableHierarchyFactory()):
        self.__hierarchy_factory = hierarchy_factory

    def create(self, batter: BatterStats) -> List[EventVariable]:
        return self.flatten_hierarchy(
            self.__hierarchy_factory.create(batter.likelihoods()).children
        )

    def create_with_ranges(self, batter: BatterStats) -> List[Tuple[float, EventVariable]]:
        return create_probability_ranges(
            self.create(batter)
        )

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
