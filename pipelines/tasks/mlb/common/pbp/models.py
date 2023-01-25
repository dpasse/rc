from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast, TypeVar, Generator, Generic


# pylint: disable=C0103
TInningState = TypeVar('TInningState', bound='InningState')
TEvent = TypeVar('TEvent', bound='Event')
TEntities = TypeVar('TEntities', bound='Entities')

@dataclass
class InningState():
    outs: int
    bases: List[int]

    @property
    def outs_key(self: TInningState) -> str:
        return str(self.outs)

    @property
    def bases_key(self: TInningState) -> str:
        return ''.join(map(str, self.bases))

    def add(self: TInningState, obj: TInningState):
        self.outs += obj.outs
        self.bases = obj.bases.copy()

class PitchCount():
    def __init__(self, obj: Dict[str, Any]) -> None:
        for key in obj.keys():
            if key == 'balls':
                self.__balls = obj[key]
            elif key == 'strikes':
                self.__strikes = obj[key]
            else:
                setattr(self, f'__{key}', obj[key])

    def balls(self) -> int:
        return self.__balls

    def strikes(self) -> int:
        return self.__strikes

class Score():
    def __init__(self, score: Dict[str, Any]):
        self.__home = 0
        self.__away = 0

        for key in score.keys():
            if key == 'home':
                self.__home = score[key]
            elif key == 'away':
                self.__away = score[key]
            else:
                setattr(self, f'__{key}', score[key])

    @property
    def home(self) -> int:
        return self.__home

    @property
    def away(self) -> int:
        return self.__away

class BeforePitch(Generic[TEvent]):
    def __init__(self, obj: Dict[str, Any]) -> None:
        self.__after = None
        self.__pitch_event_id: Optional[int] = None
        self.__pitch_event: Optional[TEvent] = None

        for key in obj.keys():
            if key == 'bases':
                self.__bases = obj[key]
            elif key == 'after':
                self.__after = obj[key]
            elif key == 'beforePitchEvent':
                self.__pitch_event_id = obj[key]
            else:
                setattr(self, f'__{key}', obj[key])

    @property
    def bases(self) -> List[int]:
        return self.__after if self.__after else self.__bases

    @property
    def pitch_event(self) -> Optional[TEvent]:
        return self.__pitch_event

    def set_pitch_events(self, pitch_events: Dict[int, TEvent]) -> None:
        if self.__pitch_event_id:
            self.__pitch_event = pitch_events[self.__pitch_event_id]

class AfterPitch(Generic[TEvent]):
    def __init__(self, obj: Dict[str, Any]) -> None:
        self.__pitch_event_id: Optional[int] = None
        self.__pitch_event: Optional[TEvent] = None

        for key in obj.keys():
            if key == 'bases':
                self.__bases = obj[key]
            elif key == 'afterPitchEvent':
                self.__pitch_event_id = obj[key]
            else:
                setattr(self, f'__{key}', obj[key])

    @property
    def bases(self) -> List[int]:
        return self.__bases

    @property
    def pitch_event(self) -> Optional[TEvent]:
        return self.__pitch_event

    def set_pitch_events(self, pitch_events: Dict[int, TEvent]):
        if self.__pitch_event_id:
            self.__pitch_event = pitch_events[self.__pitch_event_id]

class Pitch():
    def __init__(self, pitch: Dict[str, Any]):
        self.__result: AfterPitch = AfterPitch(pitch['result'])
        self.__prior: BeforePitch = BeforePitch(pitch['prior'])

        for key in pitch.keys():
            if key == 'id':
                self.__id = pitch[key]
            elif key == 'count':
                self.__count = PitchCount(pitch[key])
            else:
                setattr(self, f'__{key}', pitch[key])

    @property
    def id(self) -> str:
        return self.__id

    @property
    def count(self) -> PitchCount:
        return self.__count

    @property
    def prior(self) -> BeforePitch:
        return self.__prior

    @property
    def result(self) -> AfterPitch:
        return self.__result

    def set_pitch_events(self, pitch_events: Dict[int, TEvent]) -> None:
        self.prior.set_pitch_events(pitch_events)
        self.result.set_pitch_events(pitch_events)

class Entities(Generic[TEntities]):
    def __init__(self: TEntities, entities: Dict[str, Any]):
        self.__outs = 0
        self.__runs = 0
        self.__type = ''
        self.__at: Optional[str] = None
        self.__attrs: List[str] = []
        self.__body = entities
        self.__moves: List[TEntities] = []

        for key in entities.keys():
            if key == 'outs':
                self.__outs = entities[key]
            elif key == 'runs':
                self.__runs = entities[key]
            elif key == 'type':
                self.__type = entities[key]
            elif key == 'at':
                self.__at = entities[key]
            elif key == 'premature':
                if entities[key]:
                    self.__attrs.append(key)
            elif key == 'moves':
                self.__moves = [Entities(move) for move in entities[key]]
            else:
                setattr(self, f'__{key}', entities[key])

    @property
    def outs(self: TEntities) -> int:
        return self.__outs

    @property
    def runs(self: TEntities) -> int:
        return self.__runs

    @property
    def type(self: TEntities) -> str:
        return self.__type

    @property
    def at(self: TEntities) -> Optional[str]:
        return self.__at

    @property
    def body(self: TEntities) -> Dict[str, Any]:
        return self.__body

    @property
    def moves(self: TEntities) -> List[TEntities]:
        return self.__moves

    def is_a(self, attr: str) -> bool:
        return attr in self.__attrs

# pylint: disable=R0902
class Event():
    def __init__(self: TEvent, event: Dict[str, Any]):
        self.__id = ''
        self.__desc = ''
        self.__type = ''
        self.__attrs = []
        self.__pitch_events: Dict[int, TEvent] = {}
        self.__pitch_event_ids: List[int] = []
        self.__pitches: List[Pitch] = []

        for key in event.keys():
            if key == 'id':
                self.__id = event[key]
            elif key == 'type':
                self.__type = event[key]
            elif key == 'desc':
                self.__desc = event[key]
            elif key in ['isInfoPlay', 'isScoringPlay', 'isPitcherChange']:
                if event[key]:
                    self.__attrs.append(key)
            elif key == 'score':
                self.__score = Score(event[key])
            elif key == 'pitches':
                self.__pitches = [
                    Pitch(obj)
                    for obj in event[key]
                ]
            elif key == 'entities':
                self.__entities = Entities(event[key])
            elif key == 'pitchEvents':
                self.__pitch_event_ids = event[key]
            else:
                setattr(self, f'__{key}', event[key])

    @property
    def id(self: TEvent) -> str:
        return self.__id

    @property
    def type(self: TEvent) -> str:
        return self.__type

    @property
    def desc(self: TEvent) -> str:
        return self.__desc

    @property
    def attrs(self: TEvent) -> List[str]:
        return self.__attrs

    @property
    def score(self: TEvent) -> Score:
        return self.__score

    @property
    def entities(self: TEvent) -> Entities:
        return self.__entities

    @property
    def pitches(self: TEvent) -> List[Pitch]:
        return self.__pitches

    @property
    def has_pitches(self: TEvent) -> bool:
        return len(self.__pitches) > 0

    @property
    def last_pitch(self: TEvent) -> Optional[Pitch]:
        if not self.has_pitches:
            return None

        return self.__pitches[-1]

    @property
    def pitch_events(self) -> Dict[int, TEvent]:
        return self.__pitch_events

    def is_a(self: TEvent, attr: str) -> bool:
        return attr in self.__attrs

    def set_pitch_events(self: TEvent, pitch_events: Dict[int, TEvent]) -> None:
        self.__pitch_events = {
            event_id: pitch_events[event_id]
            for event_id in self.__pitch_event_ids
        }

        for pitch in self.pitches:
            pitch.set_pitch_events(self.__pitch_events)

    def get_prior_state(self: TEvent) -> Optional[InningState]:
        def get_pitch_events(pitches: List[Pitch]) -> Generator[TEvent, None, None]:
            for pitch in pitches:
                if pitch.prior.pitch_event:
                    yield pitch.prior.pitch_event

                if pitch.result.pitch_event:
                    yield pitch.result.pitch_event

        if not self.has_pitches:
            return None

        outs = sum(
            pitch_event.entities.outs
            for pitch_event in get_pitch_events(self.pitches[:-1])
        )

        last_pitch = cast(Pitch, self.last_pitch)
        return InningState(
            outs,
            last_pitch.prior.bases.copy()
        )

    def get_result_state(self: TEvent) -> Optional[InningState]:
        if not self.has_pitches:
            return None

        result = cast(Pitch, self.last_pitch).result

        outs = self.entities.outs
        if result.pitch_event:
            outs += result.pitch_event.entities.outs

        return InningState(
            outs,
            result.bases.copy(),
        )

class Scoreboard():
    def __init__(self, score: Dict[str, Any]):
        self.__runs = 0
        self.__hits = 0
        self.__errors = 0
        self.__outs = 0

        for key in score.keys():
            setattr(self, f'__{key}', score[key])

    @property
    def runs(self) -> int:
        return self.__runs

    @property
    def hits(self) -> int:
        return self.__hits

    @property
    def errors(self) -> int:
        return self.__errors

    @property
    def outs(self) -> int:
        return self.__outs

class Period():
    def __init__(self, period: Dict[str, Any]):
        self.__id: str = ''
        self.__at_bat: str = ''
        self.__issues: List[str] = []
        self.__events: List[Event] = []
        self.__score: Optional[Scoreboard] = None

        for key in period.keys():
            if key == 'id':
                self.__id = period[key]
            elif key == 'atBat':
                self.__at_bat = period[key]
            elif key == 'events':
                self.__events = [Event(obj) for obj in period['events']]

                pitch_events = self.get_pitch_events()
                for event in self.__events:
                    event.set_pitch_events(pitch_events)
            elif key == 'score':
                self.__score = Scoreboard(period[key])
            else:
                setattr(self, f'__{key}', period[key])

    @property
    def id(self) -> str:
        return self.__id

    @property
    def at_bat(self) -> str:
        return self.__at_bat

    @property
    def issues(self) -> List[str]:
        return self.__issues

    @property
    def events(self) -> List[Event]:
        return self.__events

    @property
    def score(self) -> Optional[Scoreboard]:
        return self.__score

    def get_pitch_events(self):
        return {
            event.id: event
            for event in self.events
            if event.type in ['after-pitch', 'before-pitch']
        }

class Game():
    def __init__(self, game: Dict[str, Any]):
        self.__id = ''
        self.__home: str = ''
        self.__away: str = ''
        self.__periods = []

        for key in game.keys():
            if key == 'id':
                self.__id = game[key]
            elif key == 'home':
                self.__home = game[key]
            elif key == 'away':
                self.__away = game[key]
            elif key == 'periods':
                self.__periods = [
                    Period(obj)
                    for obj in game['periods']
                ]
            else:
                setattr(self, f'__{key}', game[key])

    @property
    def id(self) -> str:
        return self.__id

    @property
    def teams(self) -> List[str]:
        return [self.home, self.away]

    @property
    def home(self) -> str:
        return self.__home

    @property
    def away(self) -> str:
        return self.__away

    @property
    def periods(self) -> List[Period]:
        return self.__periods

    def is_home_team(self, team: str) -> bool:
        return team == self.home

    def is_away_team(self, team: str) -> bool:
        return team == self.away
