from typing import List, Dict, Callable
from .models import EventCodes


def handleEmptyEvent(bases: List[int]) -> List[int]:
    return bases

def handleErrorEvent(bases: List[int]) -> List[int]:
    return [1] + bases

def handleTakeBaseEvent(bases: List[int]) -> List[int]:
    if bases == [1, 1, 1]:
        return [1] + bases

    ## populate the first open base we encounter
    for i, has_runner in enumerate(bases):
        if has_runner == 0:
            bases[i] = 1
            break

    return bases

def handleSingleEvent(bases: List[int]) -> List[int]:
    return [1] + bases

def handleMediumSingleEvent(bases: List[int]) -> List[int]:
    return handleSingleEvent(bases[:1] + [0] + bases[1:])

def handleLongSingleEvent(bases: List[int]) -> List[int]:
    return handleSingleEvent([0] + bases)

def handleDoubleEvent(bases: List[int]) -> List[int]:
    return [0, 1] + bases

def handleLongDoubleEvent(bases: List[int]) -> List[int]:
    return handleDoubleEvent([0] + bases)

def handleTripleEvent(bases: List[int]) -> List[int]:
    return [0, 0, 1] + bases

def handleHomerunEvent(bases: List[int]) -> List[int]:
    return [0, 0, 0, 1] + bases

def handleGroundIntoDoublePlayEvent(bases: List[int]) -> List[int]:
    if bases == [1, 0, 0]:
        return [0, 0, 0]

    if bases == [1, 1, 0]:
        return [1, 0, 0]

    if bases == [1, 0, 1]:
        return [0, 0, 0] + [1]

    if bases == [1, 1, 1]:
        return [0, 1, 1]

    return bases

def handleNormalGroundBallEvent(bases: List[int]) -> List[int]:
    if bases == [0, 1, 1]:
        return bases

    ## if bases == [1, 0, 0]:
    ##    return bases

    ## if bases == [1, 1, 0]:
    ##    return bases

    ## if bases == [1, 1, 1]:
    ##    return bases

    return bases[:1] + [0] + bases[1:]

def handleMediumFlyEvent(bases: List[int]) -> List[int]:
    return bases[:2] + [0] + bases[2:]

def handleLongFlyEvent(bases: List[int]) -> List[int]:
    return bases[:1] + [0] + bases[1:]

class Bases():
    def __init__(self, scenario=[0, 0, 0]) -> None:
        self.__bases = scenario.copy()
        self.__base_runner_rules: Dict[EventCodes, Callable[[List[int]], List[int]]] = {
            EventCodes.Error: handleErrorEvent,
            EventCodes.Walk: handleTakeBaseEvent,
            EventCodes.HBP: handleTakeBaseEvent,
            EventCodes.ShortSingle: handleSingleEvent,
            EventCodes.MediumSingle: handleMediumSingleEvent,
            EventCodes.LongSingle: handleLongSingleEvent,
            EventCodes.ShortDouble: handleDoubleEvent,
            EventCodes.LongDouble: handleLongDoubleEvent,
            EventCodes.Triple: handleTripleEvent,
            EventCodes.HR: handleHomerunEvent,
            EventCodes.GIDP: handleGroundIntoDoublePlayEvent,
            EventCodes.NormalGroundBall: handleNormalGroundBallEvent,
            EventCodes.MediumFly: handleMediumFlyEvent,
            EventCodes.LongFly: handleLongFlyEvent,
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

class Inning():
    def __init__(self) -> None:
        self.__bases = Bases()
        self.__runs: int = 0
        self.__outs: int = 0
        self.__history: List[dict] = []

    @property
    def history(self) -> List[dict]:
        return self.__history

    def load_scenario(self, bases: List[int] = [0, 0, 0], runs: int = 0, outs: int = 0):
        self.__bases = Bases(bases)
        self.__runs = runs
        self.__outs = outs

        return self

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
            if self.__outs == 2 or not (self.__bases.is_in(double_play_scenarios)):
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
            self.__history.append({
                'bases': self.__bases.state,
                'runs': self.__runs,
                'outs': self.__outs,
                'batter': key,
                'event': event_code,
                'desc': event_code.name
            })
