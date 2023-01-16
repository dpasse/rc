import re
from typing import Optional, Tuple, Dict, Any, List, Callable
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

default_description_expressions = strike_outs_exports + \
              balk_exports + \
              pick_off_exports + \
              homerun_exports + \
              walk_exports + \
              wild_pitch_exports + \
              in_play_exports + \
              interference_exports + \
              multiple_outs_export + \
              fielders_choice_export + \
              sacrifice_exports + \
              steal_exports + \
              error_exports + \
              sub_exports

from .templates import TemplateService


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
        def have_issue_with_effort(obj: Dict[str, Any]) -> bool:
            for key in ['effort']:
                if key in obj and not is_strike_out_effort(obj[key]):
                    return True

            return False

        def have_issue_with_player(obj: Dict[str, Any]) -> bool:
            for key in ['player', 'by', 'for', 'to']:
                if key in obj and not is_player(obj[key]):
                    return True

            return False

        def have_issues_with_type(obj: Dict[str, Any]) -> bool:
            for key in ['type', 'how']:
                if key in obj and not is_event_type(obj[key]):
                    return True

            return False

        def have_issues_with_location(obj: Dict[str, Any]) -> bool:
            for key in ['at']:
                if key in obj and not is_location(obj[key]):
                    return True

            return False

        def have_issues_with_order(obj: Dict[str, Any]) -> bool:
            for key in ['order']:
                if key in obj and not sum(is_position(subset) for subset in obj[key]) > 0:
                    return True

            return False

        issues = set([])

        if have_issue_with_player(observation):
            issues.add('player')

        if have_issue_with_effort(observation):
            issues.add('effort')

        if have_issues_with_type(observation):
            issues.add('type')

        if have_issues_with_location(observation):
            issues.add('at')

        if have_issues_with_order(observation):
            issues.add('order')

        if 'moves' in observation:
            for move in observation['moves']:
                if have_issue_with_player(move):
                    issues.add('player')

                if have_issues_with_type(observation):
                    issues.add('type')

                if have_issues_with_location(observation):
                    issues.add('at')

        if len(issues) > 0:
            observation['issues'] = list(issues)

        return observation

    def post_parse(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        def clean_values(observation: Dict[str, Any]) -> Dict[str, Any]:
            for key in ['type', 'at', 'by', 'for', 'how', 'effort', 'to', 'team']:
                if key in observation:
                    observation[key] = clean_text(observation[key])

                    if key in ['type', 'at', 'how', 'effort']:
                        observation[key] = observation[key].lower()

        clean_values(observation)

        if 'moves' in observation:
            moves = observation['moves']
            for move in moves:
                clean_values(move)

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
TEMPLATE_SERVICE = TemplateService()

def parse_game(game: Dict[str, Any]) -> Dict[str, Any]:
    def clear_event(event: Dict[str, Any]) -> Dict[str, Any]:
        if 'type' in event:
            del event['type']

        return event

    def set_types_on_event(event: Dict[str, Any]) -> Dict[str, Any]:
        if not 'entities' in event:
            return event

        if not 'isInfoPlay' in event:
            return event

        if not event['entities']['type'] in ['sub-p', 'sub-f']:
            event['type'] = 'before-pitch' \
                if event['entities']['type'] in ['balk', 'picked off', 'pickoff error'] \
                else 'after-pitch'

        return event

    periods = game['periods']
    for period in periods:
        events = period['events']
        for event in events:
            event = clear_event(event)

            entities = EVENT_DESCRIPTION_PARSER.transform_into_object(event['desc'])

            if entities:
                matches_template, _ = TEMPLATE_SERVICE.validate(event['desc'], entities)
                if not matches_template:
                    if not 'issues' in entities:
                        entities['issues'] = []

                    entities['issues'].append('template')

            event['entities'] = { 'issues': ['parsing'] } if entities is None else entities

            event = set_types_on_event(event)

        events = parse_pitch_events(events)
        period['events'] = events

    game['periods'] = periods
    return game
