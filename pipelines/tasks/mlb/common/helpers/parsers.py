import re
from typing import Optional, Tuple, Dict, Any, List, Callable
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
from .templates import TemplateService


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

            return observation

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
    if entities['type'] in ['sub-p', 'sub-f']:
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
        matches_template, _ = TEMPLATE_SERVICE.validate(event['desc'], entities)
        if not matches_template:
            if not 'issues' in entities:
                entities['issues'] = []

            entities['issues'].append('template')

    event['entities'] = { 'issues': ['parsing'] } if entities is None else entities
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
        if 'premature' in entities:
            continue

        if len(event['pitches']) == 0 and entities['type'] == 'intentionally walked':
            bases = move_to_open_base(bases.copy())

        else:

            for pitch in event['pitches']:
                pitch['prior'] = { 'bases': bases.copy() }
                bases = pitch['result']['bases'].copy()

    return events

def handle_pitch_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    events = set_prior_on_pitches(events)
    events = parse_pitch_events(events)

    base_index_lookup = { 'first': 0, 'second': 1, 'third': 2 }
    pitch_events = get_pitch_events(events)

    for event in filter(lambda ev: not 'isInfoPlay' in ev, events):
        for pitch in event['pitches']:

            prior = pitch['prior']
            if not 'beforePitchEvent' in prior:
                continue

            bases = prior['bases'].copy()

            entities = pitch_events[prior['beforePitchEvent']]['entities']

            if entities['type'] == 'balk':
                bases = ([0] + bases)[:3]

            if entities['type'] == 'picked off':
                base_index = base_index_lookup[entities['at']]
                bases[base_index] = 0

            if entities['type'] == 'pickoff error':
                base_index = base_index_lookup[entities['at']]
                bases[base_index] = 1

                for i in reversed(range(0, base_index)):
                    if bases[i] == 1:
                        bases[i] = 0
                        break

            prior['after'] = bases.copy()

    return events

def parse_game(game: Dict[str, Any]) -> Dict[str, Any]:

    periods = game['periods']
    for period in periods:

        if 'issues' in period:
            del period['issues']

        events = period['events']

        for event in events:
            event = clear_event(event)
            event = set_entities_on_event(event)
            event = set_types_on_event(event)

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
