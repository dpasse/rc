import re
from typing import Optional, Tuple, Dict, Any, List, Callable
from .entities.utils import clean_text, is_event_type, is_location, is_player
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

default_description_expressions = strike_outs_exports + \
              balk_exports + \
              pick_off_exports + \
              homerun_exports + \
              wild_pitch_exports + \
              walk_exports + \
              in_play_exports + \
              interference_exports + \
              multiple_outs_export + \
              fielders_choice_export + \
              sacrifice_exports + \
              steal_exports + \
              error_exports + \
              sub_exports

class ParsingEngine():
    def __init__(self, expressions: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]]) -> None:
        self.__parse_event_expressions = expressions

    def transform_into_object(self, description: str) -> Optional[dict]:
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

    def validate(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        issues = set([])

        if 'player' in observation and not is_player(observation['player']):
            issues.add('player')

        if 'type' in observation and not is_event_type(observation['type']):
            issues.add('type')

        if 'at' in observation and not is_location(observation['at']):
            issues.add('at')

        if 'moves' in observation:
            for move in observation['moves']:
                if 'player' in move and not is_player(move['player']):
                    issues.add('player')

                if 'type' in move and not is_event_type(move['type']):
                    issues.add('type')

                if 'at' in move and not is_location(move['at']):
                    issues.add('at')

        if len(issues) > 0:
            observation['issues'] = list(issues)

        return observation

    def post_parse(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        for key in ['type', 'at', 'by']:
            if key in observation:
                observation[key] = clean_text(observation[key])

                if key in ['type', 'at']:
                    observation[key] = observation[key].lower()

        if 'moves' in observation:
            moves = observation['moves']

            outs = sum(
                1
                for move
                in moves
                if move['type'] == 'out'
            )

            if outs > 0:
                if not 'outs' in observation:
                    observation['outs'] = 0

                observation['outs'] += outs

            runs = sum(
                1
                for move
                in moves
                if move['at'] == 'home' and move['type'] != 'out'
            )

            if runs > 0:
                if not 'runs' in observation:
                    observation['runs'] = 0

                observation['runs'] += runs

        observation = self.validate(observation)

        return observation


EVENT_DESCRIPTION_PARSER = EventDescriptionParser()
DELTA_KEY = 'delta'

def parse_game(game: Dict[str, Any]) -> Dict[str, Any]:
    periods = game['periods']
    for period in periods:
        events = period['events']
        for event in events:
            if 'type' in event:
                del event['type']

            description = event['desc']
            entities = EVENT_DESCRIPTION_PARSER.transform_into_object(description)

            if entities:
                event['entities'] = entities

                if 'isInfoPlay' in event and not event['entities']['type'] in ['sub-p', 'sub-f']:
                    is_before_pitch_event = event['entities']['type'] in ['balk', 'picked off', 'pickoff error']
                    event['type'] = 'before-pitch' if is_before_pitch_event else 'after-pitch'

        events = parse_pitch_events(events)
        period['events'] = events

    game['periods'] = periods
    return game
