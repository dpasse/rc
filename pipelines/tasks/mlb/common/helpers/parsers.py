from abc import abstractmethod, ABC
import re
from typing import Optional, Tuple, Dict, Any, List, Callable, Union, cast

from .extractors import calculate_total_outs, get_pitch_events
from .entities.utils import clean_text, \
                            is_event_type, \
                            is_location, \
                            is_player, \
                            is_position, \
                            is_strike_out_effort
from .entities import steal_exports, \
                      in_play_exports, \
                      strike_outs_exports, \
                      homerun_exports, \
                      walk_exports, \
                      sub_exports, \
                      multiple_outs_export, \
                      fielders_choice_export, \
                      wild_pitch_exports, \
                      error_exports, \
                      sacrifice_exports, \
                      balk_exports, \
                      pick_off_exports, \
                      interference_exports
from .entities.tie_pitch_events import parse_pitch_events
from ..pbp.models import Entities
from .templates import TemplateService


default_description_expressions =  sacrifice_exports + \
            walk_exports + \
            strike_outs_exports + \
            balk_exports + \
            pick_off_exports + \
            homerun_exports + \
            wild_pitch_exports + \
            in_play_exports + \
            interference_exports + \
            multiple_outs_export + \
            fielders_choice_export + \
            sacrifice_exports + \
            steal_exports + \
            error_exports + \
            sub_exports

class AbstractValidator(ABC):
    def __init__(self, identifier: str, keys: List[str]) -> None:
        self.__identifier = identifier
        self.__keys = keys

    @property
    def identifier(self) -> str:
        return self.__identifier

    @abstractmethod
    def is_item_valid(self, item: Union[List[str], str]) -> bool:
        pass

    def validate(self, obj: Dict[str, Any]) -> bool:
        for key in self.__keys:
            if not key in obj:
                continue

            if not self.is_item_valid(obj[key]):
                return False

        return True

class EffortValidator(AbstractValidator):
    def __init__(self) -> None:
        super().__init__('effort', ['effort'])

    def is_item_valid(self, item: Union[List[str], str]) -> bool:
        return is_strike_out_effort(cast(str, item))

class PlayerValidator(AbstractValidator):
    def __init__(self) -> None:
        super().__init__('player', ['player', 'by', 'for', 'to'])

    def is_item_valid(self, item: Union[List[str], str]) -> bool:
        return is_player(cast(str, item))

class TypeValidator(AbstractValidator):
    def __init__(self) -> None:
        super().__init__('type', ['type', 'how'])

    def is_item_valid(self, item: Union[List[str], str]) -> bool:
        return is_event_type(cast(str, item))

class LocationValidator(AbstractValidator):
    def __init__(self) -> None:
        super().__init__('at', ['at'])

    def is_item_valid(self, item: Union[List[str], str]) -> bool:
        return is_location(cast(str, item))

class OrderValidator(AbstractValidator):
    def __init__(self) -> None:
        super().__init__('order', ['order'])

    def is_item_valid(self, item: Union[List[str], str]) -> bool:
        return sum(is_position(subset) for subset in cast(List[str], item)) > 0

class GameValidator():
    def __init__(self) -> None:
        self.__validators: List[AbstractValidator] = [
            EffortValidator(),
            PlayerValidator(),
            TypeValidator(),
            LocationValidator(),
            OrderValidator(),
        ]

    def run(self, observation: Dict[str, Any]) -> List[str]:
        issues = []
        for validator in self.__validators:
            if not validator.validate(observation):
                issues.append(validator.identifier)

        return issues

    def validate(self, observation: Dict[str, Any]) -> List[str]:
        issues = []
        issues.extend(
            self.run(observation)
        )

        if 'moves' in observation:
            for move in observation['moves']:
                issues.extend(
                    [f'move.{item}' for item in self.run(move)]
                )

        return issues

class GameCleaner():
    def __init__(self) -> None:
        self.__keys = ['type', 'at', 'by', 'for', 'how', 'effort', 'to', 'team']
        self.__to_lower = set(['type', 'at', 'how', 'effort'])

    def clean_object(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        for key in self.__keys:
            if not key in observation:
                continue

            observation[key] = clean_text(observation[key])
            if key in self.__to_lower:
                observation[key] = observation[key].lower()

        return observation

    def clean(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        observation = self.clean_object(observation)

        if 'moves' in observation:
            for move in observation['moves']:
                move = self.clean_object(move)

        return observation

class ParsingEngine():
    def __init__(self, expressions: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]]) -> None:
        self.__parse_event_expressions = expressions

    def pre_parse(self, description:str) -> str:
        return description

    def transform_into_object(self, description: str) -> Optional[dict]:
        description = self.pre_parse(description)
        for expression, mapping_function in self.__parse_event_expressions:
            match = re.search(expression, description)
            observation = self.post_parse(mapping_function(list(match.groups()))) if match else None
            if observation:
                return observation

        return None

    def post_parse(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        return observation

class EventDescriptionParser(ParsingEngine):
    def __init__(self, expressions: Optional[List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]]] = None) -> None:
        super().__init__(default_description_expressions if expressions is None else expressions)

        self.__validator = GameValidator()
        self.__cleaner = GameCleaner()

    def pre_parse(self, description:str) -> str:
        description = re.sub(r'(first|second|third|left|right|center)\.', r'\g<1> ,', description).strip()
        return description

    def validate(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        issues = self.__validator.validate(observation)
        if len(issues) > 0:
            observation['issues'] = issues

        return observation

    def post_parse(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        self.__cleaner.clean(observation)

        if 'moves' in observation:
            outs = 0
            runs = 0

            for move in observation['moves']:
                if move['type'] == 'out':
                    outs += 1
                elif move['at'] == 'home':
                    runs += 1

            if outs > 0:
                if not 'outs' in observation:
                    observation['outs'] = 0

                observation['outs'] += outs

            if runs > 0:
                if not 'runs' in observation:
                    observation['runs'] = 0

                observation['runs'] += runs

        observation = self.validate(observation)
        return observation

class BaseRunners():
    def __init__(self) -> None:
        self.__base_index_lookup = {
            'first': 0,
            'second': 1,
            'third': 2,
            'home': 3,
        }

    def trim(bases: List[int]) -> List[int]:
        return bases[:3]

    def play(self, entities: Dict[str, Any], current_bases_state: List[int]) -> List[int]:
        model = Entities(entities)
        bases = current_bases_state.copy()

        if model.type == 'balk':
            return BaseRunners.trim([0] + bases)

        if model.type == 'picked off' and model.at:
            base_index = self.__base_index_lookup[model.at]
            bases[self.__base_index_lookup[model.at]] = 0

            return bases

        if model.type == 'pickoff error':
            ## order by bases, move the first guy... move the next...
            players_moved = set()
            for move in sorted(model.moves, key=lambda mv: self.__base_index_lookup[mv.at], reverse=True):
                player = move.body['player']
                if player in players_moved:
                    continue

                if move.type == 'advanced':
                    base_index = self.__base_index_lookup[move.at]
                    if base_index < 3:
                        bases[base_index] = 1

                    for i in reversed(range(0, base_index)):
                        if bases[i] == 1:
                            bases[i] = 0
                            break

                    players_moved.add(player)
                else:
                    print('not supported!', move)

        return bases

EVENT_DESCRIPTION_PARSER = EventDescriptionParser()
TEMPLATE_SERVICE = TemplateService()

def clear_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if 'type' in event:
        del event['type']

    return event

def set_types_on_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if 'isPitcherChange' in event:
        event['isInfoPlay'] = True

    if not 'isInfoPlay' in event:
        return event

    entities = event['entities']
    if entities['type'] in ['sub-p', 'sub-f', 'dropped foul ball']:
        return event

    if entities['type'] in ['picked off', 'pickoff error']:
        by_player = re.search(r'(?:picked off|pickoff error) by (pitcher|catcher)', event['desc'])
        if by_player and by_player.group(1).lower() == 'catcher':
            event['type'] = 'after-pitch'

            return event

    event['type'] = 'before-pitch' \
        if entities['type'] in ['balk', 'picked off', 'pickoff error'] \
        else 'after-pitch'

    return event

def set_entities_on_event(event: Dict[str, Any]) -> Dict[str, Any]:
    entities = EVENT_DESCRIPTION_PARSER.transform_into_object(event['desc'])

    if entities:
        matches_template, template = TEMPLATE_SERVICE.validate(event['desc'], entities)
        if not matches_template:
            if not 'issues' in entities:
                entities['issues'] = []

            entities['issues'].append('template')
            entities['issues'].append(template)
    else:
        entities = { 'issues': ['parsing'] }

    event['entities'] = entities
    return event

def set_prior_on_pitches(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def move_to_open_base(bases: List[int]) -> List[int]:
        for i, base in enumerate(bases):
            if base == 0:
                bases[i] = 1
                break

        return bases

    bases: List[int] = [0, 0, 0]
    for event in events:
        if 'isInfoPlay' in event:
            continue

        if not 'pitches' in event:
            event['pitches'] = []

        entities = event['entities']

        if len(event['pitches']) == 0 and entities['type'] == 'intentionally walked':
            bases = move_to_open_base(bases.copy())

        else:

            for pitch in event['pitches']:
                pitch['prior'] = { 'bases': bases.copy() }
                bases = pitch['result']['bases'].copy()

    return events

def correct_bases_when_prior_pitch_event_exists(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    base_runners = BaseRunners()

    pitch_events = get_pitch_events(events)
    for event in filter(lambda ev: not 'isInfoPlay' in ev, events):
        for pitch in event['pitches']:

            prior = pitch['prior']
            if 'beforePitchEvent' in prior:
                prior['after'] = base_runners.play(
                    pitch_events[prior['beforePitchEvent']]['entities'],
                    prior['bases'].copy(),
                )

    return events

def handle_pitch_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    events = set_prior_on_pitches(events)
    events = parse_pitch_events(events)
    events = correct_bases_when_prior_pitch_event_exists(events)

    return events

def parse_game(game: Dict[str, Any]) -> Dict[str, Any]:
    periods = game['periods']

    for period in periods:
        if not 'events' in period:
            period['events'] = []

        for event in period['events']:
            event = clear_event(event)
            event = set_entities_on_event(event)
            event = set_types_on_event(event)

    for period in periods:
        if 'issues' in period:
            del period['issues']

        events = period['events']
        events = handle_pitch_events(events)

        issues = []
        outs = calculate_total_outs(events)
        if outs > 3 or (outs < 3 and period['atBat'] != periods[-1]['atBat']):
            issues.append('outs')

        for event in events:
            if 'isInfoPlay' in event:
                continue

            for pitch in (event['pitches'] if 'pitches' in event else []):
                if sum(pitch['result']['bases']) - sum(pitch['prior']['bases']) > 1:
                    ## 2+ baserunners appear...
                    issues.append('bases')
                    break

        if len(issues) > 0:
            period['issues'] = issues

        period['score']['outs'] = outs
        period['events'] = events

    game['periods'] = periods
    return game
