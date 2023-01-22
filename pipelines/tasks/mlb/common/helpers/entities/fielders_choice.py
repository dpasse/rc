from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras, create_player_observation


# pylint: disable=R0801

def handle_fielders_choice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at=extras[0],
        extras=extras[1:]
    )

def handle_fielders_choice_wide(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        extras=extras,
    )

def handle_wide_fielders_choice(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': groups[1],
    }

    observation.update(
        handle_extras(split_text(groups[0]))
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]]  = [
    (r'^(.+?) ((?:(?:ground|lin|fli|bunt)ed|hit) into fielder\'s choice) to (.+)', handle_fielders_choice),
    (r'^(.+?) ((?:(?:ground|lin|fli|bunt)ed|hit) into fielder\'s choice)(.+)', handle_fielders_choice_wide),
    (r'(.+? (fielder\'s indifference|runner\'s fielder\'s choice).+)', handle_wide_fielders_choice),
]
