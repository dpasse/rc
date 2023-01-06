from .models import EventCodes


def handleEmptyEvent(bases: list):
    return bases

def handleErrorEvent(bases: list):
    return [1] + bases

def handleTakeBaseEvent(bases: list):
    if bases == [1, 1, 1]:
        return [1] + bases

    ## populate the first open base we encounter
    for i, has_runner in enumerate(bases):
        if has_runner == 0:
            bases[i] = 1
            break

    return bases

def handleSingleEvent(bases: list):
    return [1] + bases

def handleMediumSingleEvent(bases: list):
    return handleSingleEvent(bases[:1] + [0] + bases[1:])

def handleLongSingleEvent(bases: list):
    return handleSingleEvent([0] + bases)

def handleDoubleEvent(bases: list):
    return [0, 1] + bases

def handleLongDoubleEvent(bases: list):
    return handleDoubleEvent([0] + bases)

def handleTripleEvent(bases: list):
    return [0, 0, 1] + bases

def handleHomerunEvent(bases: list):
    return [0, 0, 0, 1] + bases

def handleGroundIntoDoublePlayEvent(bases: list):
    if bases == [1, 0, 0]:
        return [0, 0, 0]

    if bases == [1, 1, 0]:
        return [1, 0, 0]

    if bases == [1, 0, 1]:
        return [0, 0, 0] + [1]

    if bases == [1, 1, 1]:
        return [0, 1, 1]

    return bases

def handleNormalGroundBallEvent(bases: list):
    if bases == [0, 1, 1]:
        return bases

    ## if bases == [1, 0, 0]:
    ##    return bases

    ## if bases == [1, 1, 0]:
    ##    return bases

    ## if bases == [1, 1, 1]:
    ##    return bases

    return bases[:1] + [0] + bases[1:]

def handleMediumFlyEvent(bases: list):
    return bases[:2] + [0] + bases[2:]

def handleLongFlyEvent(bases: list):
    return bases[:1] + [0] + bases[1:]

class Inning():

    def __init__(self) -> None:
        self.__bases = [0, 0, 0]
        self.__runs = 0
        self.__outs = 0

        self.__base_runner_rules = {
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

        self.__history = []

    @property
    def history(self):
        return self.__history

    def load_scenario(self, bases = [0, 0, 0], runs = 0, outs = 0):
        self.__bases = bases.copy()
        self.__runs = runs
        self.__outs = outs

        return self

    def is_over(self) -> bool:
        return self.__outs >= 3

    def handle_runners_on_base(self, event_code):
        bases = self.__bases.copy()
        if not event_code in self.__base_runner_rules:
            return bases

        return self.__base_runner_rules[event_code](bases)

    def get_current_state(self):
        return {
            'bases': self.__bases,
            'runs': self.__runs,
            'outs': self.__outs,
        }

    def execute(self, key: str, event_code: EventCodes):
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

            current_state = self.get_current_state()
            current_state.update({
                'batter': key,
                'event': event_code,
                'desc': event_code.name
            })

            self.__history.append(current_state)
