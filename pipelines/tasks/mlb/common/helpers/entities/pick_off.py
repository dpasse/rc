import re
from typing import Dict, Any, List, Tuple, Callable
from .utils import create_player_observation, split_text

def handle_pick_off(groups: List[str]) -> Dict[str, Any]:
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at= groups[2] if len(groups) > 2 else None,
        outs=1
    )

def handle_wide_pick_off_error(groups) -> Dict[str, Any]:
    text = groups[0]

    player = 'not found'
    for pitcher_match_expression in [
        r'(?:pickoff error) by (?:pitcher|catcher|(?:first|second|third) baseman) (.+?)(?:,|$)',
        r'(?:pickoff error) by (.+?)(?:,|$)',
    ]:
        pitcher_match = re.search(pitcher_match_expression, text)
        if pitcher_match:
            player = re.sub(r'[.]+$', '', pitcher_match.group(1))
            break

    observation = create_player_observation(
        player=player,
        event_type=groups[1],
        extras=split_text(text),
    )

    return observation

def handle_pick_off_error(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[3])
    observation = create_player_observation(
        player=groups[0],
        event_type=groups[2],
        at=groups[1],
        extras=extras[1:]
    )

    observation['by'] = extras[0]

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+? (pickoff error).+)', handle_wide_pick_off_error),
    #(r'^(.+?) to (.+?) on (pickoff error) by (?:pitcher|catcher|(?:first|second|third) baseman)(.+)', handle_pick_off_error),
    (r'^(.+?) (picked off)(?: and caught stealing|) (.+)', handle_pick_off),
]
