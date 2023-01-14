from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras, create_player_observation

def handle_fielders_choice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at=extras[0],
        extras=extras[1:]
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
    (r'^(.+?) ((?:ground|lin|fli)ed into fielder\'s choice) to (.+)', handle_fielders_choice),
    (r'(.+? (fielder\'s indifference|runner\'s fielder\'s choice).+)', handle_wide_fielders_choice),
]
