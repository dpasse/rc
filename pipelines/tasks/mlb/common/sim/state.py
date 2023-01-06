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

class Inning():

    def __init__(self) -> None:
        self.__bases: List[int] = [0, 0, 0]
        self.__runs: int = 0
        self.__outs: int = 0
        self.__history: List[dict] = []
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
    def history(self) -> List[dict]:
        return self.__history

    def load_scenario(self, bases: List[int] = [0, 0, 0], runs: int = 0, outs: int = 0):
        self.__bases = bases.copy()
        self.__runs = runs
        self.__outs = outs

        return self

    def is_over(self) -> bool:
        return self.__outs >= 3

    def handle_runners_on_base(self, event_code: EventCodes) -> List[int]:
        bases = self.__bases.copy()
        if not event_code in self.__base_runner_rules:
            return bases

        return self.__base_runner_rules[event_code](bases)

    def get_current_state(self) -> dict:
        return {
            'bases': self.__bases,
            'runs': self.__runs,
            'outs': self.__outs,
        }

    def execute(self, key: str, event_code: EventCodes) -> None:
        ## correct GIDP Event when it doesnt fit scenario
        if event_code == EventCodes.GIDP:
            if self.__outs == 2 or not (self.__bases == [1, 0, 0] or self.__bases == [1, 1, 0] or self.__bases == [1, 0, 1] or self.__bases == [1, 1, 1]):
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
            bases = self.handle_runners_on_base(event_code)

            self.__runs += sum(bases[3:])
            self.__bases = bases[:3]

            self.__history.append({
                'bases': self.__bases.copy(),
                'runs': self.__runs,
                'outs': self.__outs,
                'batter': key,
                'event': event_code,
                'desc': event_code.name
            })
