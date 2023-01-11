import re
from typing import Optional, Tuple, Dict, Any, List, Callable


def handle_steals(groups: List[str]) -> Dict[str, Any]:
    base = groups[2].split(',')
    return {
        'player': groups[0],
        'type': groups[1],
        'base': base[0]
    }

def handle_in_play(groups: List[str]) -> Dict[str, Any]:
    extras = groups[2].split(',')

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'to': extras[0],
    }

    moves = []
    for extra in extras[1:]:
        match = None
        for expression in [r'^ *(.+?) to (.+)', r'^ *(.+?) (scored)']:
            match = re.search(expression, extra)
            if match:
                moves.append({
                    'player': match.group(1),
                    'to': 'home' if match.group(2) == 'scored' else match.group(2)
                })

                break

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_strike_outs(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': groups[1],
        'base': groups[2]
    }

def handle_homerun(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': groups[1],
        'to': groups[2]
    }

def handle_walk(groups: List[str]) -> Dict[str, Any]:
    extras = groups[1].split(',')

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': extras[0],
    }

    moves = []
    for extra in extras[1:]:
        match = None
        for expression in [r'^ *(.+?) to (.+)', r'^ *(.+?) (scored)']:
            match = re.search(expression, extra)
            if match:
                moves.append({
                    'player': match.group(1),
                    'to': 'home' if match.group(2) == 'scored' else match.group(2)
                })

                break

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_subs(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': 'sub-p' if groups[1] == 'pitching' else 'sub-f',
    }

class EventDescriptionParser():
    def __init__(self) -> None:
        self.__parse_event_expressions: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
            (r'^(.+?) (hit for|in|as|catching|pitching)', handle_subs),
            (r'^(.+?) (caught stealing|stole) (.+?)\.', handle_steals),
            (r'^(.+?) ((?:singl|doubl|tripl)ed) to (.+?)\.', handle_in_play),
            (r'^(.+?) ((?:lin|ground|fli|foul|popp)ed out) to (.+?)\.', handle_in_play),
            (r'^(.+?) (struck out) (.+?)\.', handle_strike_outs),
            (r'^(.+?) ((?:homer)ed) to (\w+)', handle_homerun),
            (r'^(.+?) (walked.*?)\.', handle_walk),

            #### good
            ##(r'^(.+?) reached on (infield single) to (.+?)\.', lambda groups: { 'player': groups[0], 'type': groups[1], 'to': groups[2] }),
            ## (r'(wild pitch) by (.+?)\.', lambda groups: { 'player': groups[0], 'type': groups[1] }),
        ]

    def transform_into_object(self, description: str) -> Optional[dict]:
        description_as_object = None
        for expression, mapping_function in self.__parse_event_expressions:
            match = re.search(expression, description)
            if match:
                description_as_object = mapping_function(list(match.groups()))

        return description_as_object
