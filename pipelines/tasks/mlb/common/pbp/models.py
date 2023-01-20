from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast, TypeVar, Tuple

# pylint: disable=C0103
TInningState = TypeVar('TInningState', bound='InningState')

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

class Score():
    def __init__(self, score: Dict[str, Any]):
        self.__home = 0
        self.__away = 0

        for key in score.keys():
            setattr(self, f'__{key}', score[key])

    @property
    def home(self) -> int:
        return self.__home

    @property
    def away(self) -> int:
        return self.__away

# pylint: disable=C0103
TEvent = TypeVar('TEvent', bound='Event')

# pylint: disable=R0902
class Event():
    def __init__(self: TEvent, event: Dict[str, Any]):
        self.__id = ''
        self.__desc = ''
        self.__type = ''
        self.__attrs = []
        self.__pitch_events: Dict[int, TEvent] = {}
        self.__pitch_event_ids: List[int] = []
        self.__pitches: List[Dict[str, Any]] = []
        self.__entities: Dict[str, Any] = {}

        for key in event.keys():
            if key == 'id':
                self.__id = event[key]
            elif key == 'type':
                self.__type = event[key]
            elif key in ['isInfoPlay', 'isScoringPlay', 'isPitcherChange']:
                if event[key]:
                    self.__attrs.append(key)
            elif key == 'score':
                self.__score = Score(event[key])
            elif key == 'pitches':
                self.__pitches = event[key]
            elif key == 'entities':
                self.__entities = event[key]
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
    def entities(self: TEvent) -> Dict[str, Any]:
        return self.__entities

    @property
    def pitches(self: TEvent) -> List[Dict[str, Any]]:
        return self.__pitches

    @property
    def has_pitches(self: TEvent) -> bool:
        return len(self.__pitches) > 0

    @property
    def last_pitch(self: TEvent) -> Optional[Dict[str, Any]]:
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

    def get_prior_state(self: TEvent) -> Optional[InningState]:
        def get_pitch_event_ids(pitches: List[Dict[str, Any]]):
            length = len(pitches)
            for i, pitch in enumerate(pitches[:-1]):
                prior = pitch['prior']
                if 'beforePitchEvent' in prior:
                    yield prior['beforePitchEvent']

                if length != i:
                    result = pitch['result']
                    if 'afterPitchEvent' in result:
                        yield result['afterPitchEvent']

        if not self.has_pitches:
            return None

        outs = 0
        for id in get_pitch_event_ids(self.pitches):
            entities = self.pitch_events[id].entities
            outs += entities['outs'] if 'outs' in entities else 0

        last_pitch = cast(Dict[str, Any], self.last_pitch)
        return InningState(
            outs, (
                last_pitch['prior']['after']
                if 'after' in last_pitch['prior']
                else last_pitch['prior']['bases']
            ).copy()
        )

    def get_result_state(self: TEvent) -> Optional[InningState]:
        if not self.has_pitches:
            return None

        outs = self.entities['outs'] if 'outs' in self.entities else 0

        result = cast(Dict[str, Any], self.last_pitch)['result']
        if 'afterPitchEvent' in result:
            entities = self.pitch_events[result['afterPitchEvent']].entities
            outs += entities['outs'] if 'outs' in entities else 0

        return InningState(
            outs,
            result['bases'].copy(),
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
        self.__home: str = cast(str, game['home'])
        self.__away: str = cast(str, game['away'])
        self.__periods = []

        for key in game.keys():
            if key == 'id':
                self.__id = game[key]
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
