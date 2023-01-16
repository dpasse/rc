import re
from typing import Dict, Any, List, Tuple, Callable
from .utils import clean_text, create_player_observation


def clean_location(text: str) -> str:
    return re.sub(r'(base|field)', '', text).strip()

def handle_position_sub(groups: List[str]) -> Dict[str, Any]:
    is_pitch = clean_text(groups[1]).startswith('pitch')
    return create_player_observation(
        player=groups[0],
        event_type='sub-p' if is_pitch else 'sub-f',
        at=clean_location(groups[1]),
    )

def handle_player_sub(groups: List[str]) -> Dict[str, Any]:
    observation = create_player_observation(
        player=groups[0],
        event_type='sub-f'
    )

    observation['for'] = groups[1]

    return observation

def handle_pitcher_sub(groups: List[str]) -> Dict[str, Any]:
    observation = create_player_observation(
        player=groups[0],
        event_type=groups[1]
    )

    observation['to'] = groups[2]

    return observation

def handle_pitcher_sub_with_team(groups: List[str]) -> Dict[str, Any]:
    observation = create_player_observation(
        player=groups[0],
        event_type='sub-p'
    )

    observation['team'] = groups[1]

    return observation

def handle_default_sub(groups: List[str]) -> Dict[str, Any]:
    is_pitch = clean_text(groups[1]).startswith('pitch')
    return create_player_observation(
        player=groups[0],
        event_type='sub-p' if is_pitch else 'sub-f',
    )

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) (?:a[st]|in) (.+)', handle_position_sub),
    (r'^(.+?) (?:hit|ran) for (.+)', handle_player_sub),
    (r'^(.+?) pitching for (.+)', handle_pitcher_sub_with_team),
    (r'^(.+?) (catching)', handle_default_sub),
    (r'^(.+?) (pitches) to (.+)', handle_pitcher_sub),
]
