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
        self.bases = [0, 0, 0]
        self.runs = 0
        self.outs = 0

        self.base_runner_rules = {
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

        self.history = []

    def load_scenario(self, bases = [0, 0, 0], runs = 0, outs = 0):
        self.bases = bases.copy()
        self.runs = runs
        self.outs = outs

        return self

    def is_over(self) -> bool:
        return self.outs >= 3

    def handle_runners_on_base(self, event_code):
        bases = self.bases.copy()
        if not event_code in self.base_runner_rules:
            return bases

        return self.base_runner_rules[event_code](bases)

    def get_current_state(self):
        return {
            'bases': self.bases,
            'runs': self.runs,
            'outs': self.outs,
        }

    def execute(self, event_code: EventCodes):
        ## correct GIDP Event when it doesnt fit scenario
        if event_code == EventCodes.GIDP:
            if self.outs == 2 or not (self.bases == [1, 0, 0] or self.bases == [1, 1, 0] or self.bases == [1, 0, 1] or self.bases == [1, 1, 1]):
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
            self.outs += 2 if event_code == EventCodes.GIDP else 1

        if not self.is_over():
            bases = self.handle_runners_on_base(event_code)

            self.runs += sum(bases[3:])
            self.bases = bases[:3]

            current_state = self.get_current_state()
            current_state.update({
                'event': event_code,
                'desc': event_code.name
            })

            self.history.append(current_state)
