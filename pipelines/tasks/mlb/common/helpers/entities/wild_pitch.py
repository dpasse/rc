import re
from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, clean_text


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
        r'^ *(.+?) stole (.+)',
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

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+? (?:wild pitch|passed ball).+)', handle_wild_pitch),
]
