from typing import List, Optional
from dataclasses import dataclass

from .models.event_codes import EventCodes
from .states import get_states, StateLookupType, BasesType


class Bases():
    def __init__(self, scenario: Optional[BasesType] = None) -> None:
        self.__bases = (scenario if scenario else [0, 0, 0]).copy()
        self.__base_runner_rules: StateLookupType = get_states()

    @property
    def state(self) -> BasesType:
        return self.__bases.copy()

    def matches(self, scenario: BasesType) -> bool:
        return self.__bases == scenario

    def is_in(self, scenarios: List[BasesType]) -> bool:
        for scenario in scenarios:
            if self.matches(scenario):
                return True

        return False

    def play_event(self, event_code: EventCodes) -> int:
        if not event_code in self.__base_runner_rules:
            return 0

        ## run rules
        bases = self.__base_runner_rules[event_code](self.__bases.copy())

        ## add up runs
        runs = sum(bases[3:])

        ## correct state
        self.__bases = bases[:3]

        return runs

@dataclass
class InningScenario():
    bases: BasesType
    runs: int
    outs: int

@dataclass
class InningHistory():
    bases: BasesType
    runs: int
    outs: int
    batter: str
    event: EventCodes
    desc: str

class Inning():
    def __init__(self, scenario: Optional[InningScenario] = None) -> None:
        self.__bases = Bases(scenario.bases if scenario else [0, 0, 0])
        self.__runs: int = scenario.runs if scenario else 0
        self.__outs: int = scenario.outs if scenario else 0
        self.__history: List[InningHistory] = []

    @property
    def history(self) -> List[InningHistory]:
        return self.__history

    def is_over(self) -> bool:
        return self.__outs >= 3

    def execute(self, key: str, event_code: EventCodes) -> None:
        ## correct GIDP Event when it doesnt fit scenario
        if event_code == EventCodes.GIDP:
            double_play_scenarios = [
                [1, 0, 0],
                [1, 1, 0],
                [1, 0, 1],
                [1, 1, 1]
            ]
            if self.__outs == 2 or not self.__bases.is_in(double_play_scenarios):
                event_code =  EventCodes.NoAdvanceGroundBall

        if event_code in [
            EventCodes.Strikeout,
            EventCodes.ShortFly,
            EventCodes.MediumFly,
            EventCodes.LongFly,
            EventCodes.LineDriveInfieldFly,
            EventCodes.NormalGroundBall,
            EventCodes.NoAdvanceGroundBall,
            EventCodes.GIDP,
        ]:
            self.__outs += 2 if event_code == EventCodes.GIDP else 1

        if not self.is_over():
            self.__runs += self.__bases.play_event(event_code)
            self.__history.append(InningHistory(
                self.__bases.state,
                self.__runs,
                self.__outs,
                key,
                event_code,
                event_code.name
            ))
