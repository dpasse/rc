import re
from typing import Optional, Tuple, Dict, Any, List, Callable


def split_text(text: str, delimiter: str = ',') -> List[str]:
    return [
        text
        for text in map(
            lambda text: text.strip(),
            text.split(delimiter)
        )
        if len(text) > 0
    ]

def handle_moves(items: List[str]) -> List[Dict[str, Any]]:
    move_expressions = [
      r'^ *(.+?) to (.+)',
      r'^ *(.+?) (scored)',
    ]

    moves: List[Dict[str, Any]] = []
    for item in items:
        match = None
        for expression in move_expressions:
            match = re.search(expression, item)
            if match:
                moves.append({
                    'player': match.group(1),
                    'at': 'home' if match.group(2) == 'scored' else match.group(2)
                })

                break

    return moves

def handle_steals(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0]
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
        'to': extras[0],
    }

    moves = handle_moves(extras[1:])
    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_in_play_out(groups: List[str]) -> Dict[str, Any]:
    observation = handle_in_play(groups)
    observation['outs'] = 1

    return observation

def handle_strike_outs(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': groups[1],
        'effort': groups[2]
    }

def handle_homerun(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': groups[1],
        'at': groups[2]
    }

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
        'type': 'sub-p' if groups[1] == 'pitching' else 'sub-f',
    }

def handle_multiple_outs(groups: List[str]) -> Dict[str, Any]:
    observation_type = groups[1].lower()
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': observation_type,
        'outs': 2 if 'double play' in observation_type else 3,
    }

    extras = split_text(groups[2])

    observation['order'] = extras[0].split(' to ')

    moves = []
    for item in extras[1:]:
        move_match = re.search(r'^ *(.+?) (out at|doubled off|to) (.+)', item)
        if move_match:
            out_type = move_match.group(2)

            moves.append({
                'player': move_match.group(1),
                'type': 'out' if out_type in ['out at', 'doubled off'] else 'advanced',
                'at': move_match.group(3)
            })

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_fielders_choice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
    }

    moves = []
    for item in extras[1:]:
        move_match = re.search(r'^ *(.+?) (out at|doubled off|to) (.+)', item)
        if move_match:
            out_type = move_match.group(2)
            moves.append({
                'player': move_match.group(1),
                'type': 'out' if out_type in ['out at', 'doubled off'] else 'advanced',
                'at': move_match.group(3)
            })

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_wild_pitch(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': 'wild pitch',
    }

    text = groups[0]
    pitcher_match = re.search(r'wild pitch by (.+?)[,.]', text)
    if pitcher_match:
        observation['pitcher'] = pitcher_match.group(1)

    moves = []
    for item in split_text(text):
        move_match = re.search(r'^ *(.+?) to (.+?) on wild', item)
        if move_match:
            moves.append({
                'player': move_match.group(1),
                'type': 'advanced',
                'at': move_match.group(2)
            })

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

class EventDescriptionParser():
    def __init__(self) -> None:
        self.__parse_event_expressions: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
            (r'^(.+?) (hit for|in\b|as\b|catching|pitching)', handle_subs),
            (r'^(.+?) (caught stealing|stole) (.+?)\.', handle_steals),
            (r'^(.+?) ((?:singl|doubl|tripl)ed) to (.+?)\.', handle_in_play),
            (r'^(.+?) reached on (infield single) to (.+?)\.', handle_in_play),
            (r'^(.+?) ((?:lin|ground|fli|foul|popp)ed out) to (.+?)\.', handle_in_play_out),
            (r'^(.+?) ((?:ground|lin)ed into (?:double|triple) play)(.*?)\.', handle_multiple_outs),
            (r'^(.+?) ((?:ground|lin)ed into fielder\'s choice) to (.*?)\.', handle_fielders_choice),
            (r'^(.+?) (struck out) (.+?)\.', handle_strike_outs),
            (r'^(.+?) ((?:homer)ed) to (\w+)', handle_homerun),
            (r'^(.+?) (walked.*?)\.', handle_walk),
            (r'^(.+? wild pitch by .+)', handle_wild_pitch),
        ]

    def transform_into_object(self, description: str) -> Optional[dict]:
        description_as_object = None
        for expression, mapping_function in self.__parse_event_expressions:
            match = re.search(expression, description)
            if match:
                description_as_object = mapping_function(list(match.groups()))

        return description_as_object
