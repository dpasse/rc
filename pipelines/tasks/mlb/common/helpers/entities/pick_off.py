from typing import Dict, Any, List, Tuple, Callable

def handle_pick_off(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'outs': 1,
    }

    if len(groups) > 2:
        observation['at'] = groups[2]

    return observation

def handle_pick_off_error(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[2],
        'at': groups[1],
        'by': groups[3],
    }

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) to (.+?) on (pickoff error) by (?:pitcher|catcher) (.+)', handle_pick_off_error),
    (r'^(.+?) (picked off) and caught stealing (.+)', handle_pick_off),
    (r'^(.+?) (picked off) (.+)', handle_pick_off),
]
