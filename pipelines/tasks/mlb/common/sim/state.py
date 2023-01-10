from typing import List, Dict, Callable, Optional
from dataclasses import dataclass
from .models import EventCodes


def handle_empty_event(bases: List[int]) -> List[int]:
    return bases

def handle_error_event(bases: List[int]) -> List[int]:
    return [1] + bases

def handle_take_base_event(bases: List[int]) -> List[int]:
    if bases == [1, 1, 1]:
        return [1] + bases

    ## populate the first open base we encounter
    for i, has_runner in enumerate(bases):
        if has_runner == 0:
            bases[i] = 1
            break

    return bases

def handle_single_event(bases: List[int]) -> List[int]:
    return [1] + bases

def handle_medium_single_event(bases: List[int]) -> List[int]:
    return handle_single_event(bases[:1] + [0] + bases[1:])

def handle_long_single_event(bases: List[int]) -> List[int]:
    return handle_single_event([0] + bases)

def handle_double_event(bases: List[int]) -> List[int]:
    return [0, 1] + bases

def handle_long_double_event(bases: List[int]) -> List[int]:
    return handle_double_event([0] + bases)

def handle_triple_event(bases: List[int]) -> List[int]:
    return [0, 0, 1] + bases

def handle_homerun_event(bases: List[int]) -> List[int]:
    return [0, 0, 0, 1] + bases

def handle_ground_into_double_play_event(bases: List[int]) -> List[int]:
    if bases == [1, 0, 0]:
        return [0, 0, 0]

    if bases == [1, 1, 0]:
        return [1, 0, 0]

    if bases == [1, 0, 1]:
        return [0, 0, 0] + [1]

    if bases == [1, 1, 1]:
        return [0, 1, 1]

    return bases

def handle_normal_ground_ball_event(bases: List[int]) -> List[int]:
    if bases == [0, 1, 1]:
        return bases

    ## if bases == [1, 0, 0]:
    ##    return bases

    ## if bases == [1, 1, 0]:
    ##    return bases

    ## if bases == [1, 1, 1]:
    ##    return bases

    return bases[:1] + [0] + bases[1:]

def handle_medium_fly_event(bases: List[int]) -> List[int]:
    return bases[:2] + [0] + bases[2:]

def handle_long_fly_event(bases: List[int]) -> List[int]:
    return bases[:1] + [0] + bases[1:]

class Bases():
    def __init__(self, scenario: Optional[List[int]] = None) -> None:
        self.__bases = (scenario if scenario else [0, 0, 0]).copy()
        self.__base_runner_rules: Dict[EventCodes, Callable[[List[int]], List[int]]] = {
            EventCodes.Error: handle_error_event,
            EventCodes.Walk: handle_take_base_event,
            EventCodes.HBP: handle_take_base_event,
            EventCodes.ShortSingle: handle_single_event,
            EventCodes.MediumSingle: handle_medium_single_event,
            EventCodes.LongSingle: handle_long_single_event,
            EventCodes.ShortDouble: handle_double_event,
            EventCodes.LongDouble: handle_long_double_event,
            EventCodes.Triple: handle_triple_event,
            EventCodes.HR: handle_homerun_event,
            EventCodes.GIDP: handle_ground_into_double_play_event,
            EventCodes.NormalGroundBall: handle_normal_ground_ball_event,
            EventCodes.MediumFly: handle_medium_fly_event,
            EventCodes.LongFly: handle_long_fly_event,
        }

    @property
    def state(self) -> List[int]:
        return self.__bases.copy()

    def matches(self, scenario: List[int]) -> bool:
        return self.__bases == scenario

    def is_in(self, scenarios: List[List[int]]) -> bool:
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
    bases: List[int]
    runs: int
    outs: int

@dataclass
class InningHistory():
    bases: List[int]
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
