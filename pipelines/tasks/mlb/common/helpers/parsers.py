import re
from typing import Optional, Tuple, Dict, Any, List, Callable


def clean_text(text: str) -> str:
    return re.sub(r'[,.]$', '', text).strip()

def split_text(text: str, delimiter: str = r',') -> List[str]:
    return [
        text
        for text in map(
            clean_text,
            re.split(delimiter, text)
        )
        if len(text) > 0
    ]

def handle_moves(groups: List[str]) -> List[Dict[str, Any]]:
    move_expressions = [
      r'^ *(.+?) (out(?: |stretching)+at|doubled off|to) (.+)',
      r'^ *(.+?) (scored)',
    ]

    moves: List[Dict[str, Any]] = []
    for item in groups:
        match = None
        for expression in move_expressions:
            match = re.search(expression, item)
            if match:
                match_groups = match.groups()

                move_type = match_groups[1]
                moves.append({
                    'player': match_groups[0],
                    'type': 'advanced' if move_type in ['to', 'scored'] else 'out',
                    'at': 'home' if move_type == 'scored' else clean_text(match_groups[2]),
                })

                break

    return moves

def handle_outs_plus_moves(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'order':  [
            text
            for text
            in map(clean_text, re.split(r' ?to ', groups[0]))
            if len(text) > 0
        ]
    }

    moves = handle_moves(groups[1:])
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_steals(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
    }

    moves = handle_moves(extras[1:])
    if moves:
        observation['moves'] = moves

    return observation

def handle_in_play(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
    }

    moves = handle_moves(extras[1:])
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_in_play_out(groups: List[str]) -> Dict[str, Any]:
    observation = {
        'outs': 1,
    }

    observation.update(handle_in_play(groups))
    return observation

def handle_strike_outs(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': groups[1],
        'effort': groups[2],
        'outs': 1,
    }

def handle_homerun(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(
        re.sub(r'\([^)]+\)', '', groups[2]),
        r'(,| and )'
    )

    observation = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'runs': 1,
    }

    moves = handle_moves(extras[1:])
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_walk(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[1])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': extras[0],
    }

    moves = handle_moves(extras[1:])
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_subs(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': 'sub-p' if clean_text(groups[1]).startswith('pitch') else 'sub-f',
    }

def handle_multiple_outs(groups: List[str]) -> Dict[str, Any]:
    observation_type = clean_text(groups[1].lower())
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': observation_type,
        'outs': 1,
    }

    observation.update(
        handle_outs_plus_moves(split_text(groups[2]))
    )

    return observation

def handle_caught_stealing(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'outs': 1,
    }

    observation.update(
        handle_outs_plus_moves(extras[1:])
    )

    return observation

def handle_fielders_choice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0]
    }

    moves = handle_moves(extras[1:])
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_wild_pitch(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': 'wild pitch',
    }

    pitcher_match_expressions = [
        r'(?:wild pitch|passed ball) by (.+?)[,.]',
        r'on (.+?) wild pitch',
    ]

    text = groups[0]
    for pitcher_match_expression in pitcher_match_expressions:
        pitcher_match = re.search(pitcher_match_expression, text)
        if pitcher_match:
            observation['player'] = pitcher_match.group(1)
            break

    advanced_expressions = [
        r'^ *(.+?) (scored) on',
        r'^ *(.+?) to (.+?) on (?:wild|passed)',
    ]

    moves = []
    for item in split_text(text):
        for advanced_expression in advanced_expressions:
            move_match = re.search(advanced_expression, item)
            if move_match:
                match_groups = list(move_match.groups())
                at_base = clean_text(match_groups[1])
                moves.append({
                    'player': match_groups[0],
                    'type': 'advanced',
                    'at': 'home' if at_base == 'scored' else at_base,
                })

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_error(groups: List[str]) -> Dict[str, Any]:
    at_base = clean_text(groups[1])
    return {
        'player': groups[0],
        'type': groups[2],
        'at': 'home' if at_base == 'scored' else at_base,
    }

def handle_sacrifice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'outs': 1,
    }

    moves = handle_moves(extras)
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_balk(groups: List[str]) -> Dict[str, Any]:
    extras = re.sub(r'on a balk', '', groups[0]).split(',')
    observation: Dict[str, Any] = {
        'type': 'balk',
    }

    moves = handle_moves(extras)
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

class EventDescriptionParser():
    def __init__(self) -> None:
        self.__parse_event_expressions: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
            (r'^(.+?) (stole) (.+)', handle_steals),
            (r'^(.+?) (caught stealing) (.+)', handle_caught_stealing),
            (r'^(.+?) ((?:singl|doubl|tripl)ed) to (.+)', handle_in_play),
            (r'^(.+?) reached on (infield single|bunt single) to (.+)', handle_in_play),
            (r'^(.+?) ((?:lin|ground|fli|foul|popp)ed out) to (.+)', handle_in_play_out),
            (r'^(.+?) ((?:ground|lin)ed into (?:double|triple) play)(.+)', handle_multiple_outs),
            (r'^(.+?) ((?:ground|lin)ed into fielder\'s choice) to (.+)', handle_fielders_choice),
            (r'^(.+?) (struck out) (.+?)\.', handle_strike_outs),
            (r'^(.+?) ((?:homer)ed) to (.+?)\.', handle_homerun),
            (r'^(.+?) ((?:(?:intentionally |)walked|hit by pitch).*)', handle_walk),
            (r'^(.+?)(?: |hit)+(sacrifice fly|sacrificed) to (.+)', handle_sacrifice),
            (r'^(.+?)(?: |safe at)+(.+?) on ((?:fielding|throwing) error)', handle_error),
            (r'^(.+?) ((?:hit|ran) for|in\b|a[st]\b|catching|pitch(?:ing|es to))', handle_subs),
            (r'^(.+? (?:wild pitch|passed ball).+)', handle_wild_pitch),
            (r'^(.+? (?:balk).+)', handle_balk),
        ]

    def transform_into_object(self, description: str) -> Optional[dict]:
        description_as_object = None
        for expression, mapping_function in self.__parse_event_expressions:
            match = re.search(expression, description)
            if match:
                description_as_object = mapping_function(list(match.groups()))

                if 'type' in description_as_object:
                    description_as_object['type'] = clean_text(description_as_object['type']).lower()

                if 'at' in description_as_object:
                    description_as_object['at'] = clean_text(description_as_object['at']).lower()

                if 'moves' in description_as_object:
                    outs = sum(
                        1
                        for move
                        in description_as_object['moves']
                        if move['type'] == 'out'
                    )

                    if outs > 0:
                        if not 'outs' in description_as_object:
                            description_as_object['outs'] = 0

                        description_as_object['outs'] += outs

                    runs = sum(
                        1
                        for move
                        in description_as_object['moves']
                        if move['at'] == 'home'
                    )

                    if runs > 0:
                        if not 'runs' in description_as_object:
                            description_as_object['runs'] = 0

                        description_as_object['runs'] += runs

                break

        return description_as_object
