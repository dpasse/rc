from typing import Dict, Any, List, Callable, Tuple
from .utils import split_text, create_player_observation


def handle_strike_outs_no_effort(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation = create_player_observation(
        player=groups[0],
        event_type='struck out',
        extras=extras,
    )

    is_out = True
    for move in observation['moves']:
        if observation['player'] == move['player'] and move['type'] == 'advanced':
            is_out = False

    if is_out:
        observation['outs'] = 1

    return observation

def handle_strike_outs(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation = create_player_observation(
        player=groups[0],
        event_type='struck out',
        extras=extras[1:],
        outs=1
    )

    observation['effort'] = extras[0]

    return observation

def handle_called_out_on_strikes(groups: List[str]) -> Dict[str, Any]:
    observation = create_player_observation(
        player=groups[0],
        event_type='struck out',
        outs=1
    )

    observation['effort'] = 'called out'

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) (struck out)(,.+)', handle_strike_outs_no_effort),
    (r'^(.+?) (struck out)(.+)', handle_strike_outs),
    (r'^(.+?) called out on strikes\.', handle_called_out_on_strikes),
]
