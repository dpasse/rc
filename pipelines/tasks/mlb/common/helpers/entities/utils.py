import re
from typing import Optional, Tuple, Dict, Any, List


Positions = set([
    'catcher',
    'first',
    'second',
    'shortstop',
    'third',
    'left',
    'center',
    'right',
    'pitcher',
])

def create_player_observation(player: str, event_type: str, at: Optional[str] = None, outs: Optional[int] = None, runs: Optional[int] = None, extras: Optional[List[str]] = None):
    observation: Dict[str, Any] = {
        'player': player,
        'type': event_type,
    }

    if at:
        observation['at'] = at

    if outs:
        observation['outs'] = outs

    if runs:
        observation['runs'] = runs

    if extras and len(extras) > 0:
        observation.update(
            handle_extras(extras)
        )

    return observation

def search(expressions: List[str], text: str) -> Optional[re.Match[str]]:
    for expression in expressions:
        match = re.search(expression, text)
        if match:
            return match

    return None

def replace(expressions: List[Tuple[str, str]], text: str) -> str:
    copy_of_text = text[:]
    for expression, replace_with in expressions:
        copy_of_text = re.sub(expression, replace_with, copy_of_text)

    return copy_of_text

def clean_text(text: str) -> str:
    return re.sub(r'[,.]$', '', text).strip()

def split_text(text: str, delimiter: str = r',|\band\b') -> List[str]:
    return [
        text
        for text in map(
            clean_text,
            re.split(delimiter, text)
        )
        if len(text) > 0
    ]

def handle_moves(groups: List[str]) -> List[Dict[str, Any]]:
    moves: List[Dict[str, Any]] = []
    for item in groups:
        match = search([
                r'^ *(.+?) (thrown out at|out(?: |stretching)+at|doubled off|caught stealing|safe at|to) (.+)',
                r'^ *(.+?) (thrown out|scored)',
            ],
            item
        )

        if match:
            match_groups = match.groups()

            player = match_groups[0]
            move_type = match_groups[1]

            at = None
            if move_type == 'scored' or len(match_groups) == 3:
                at = 'home' if move_type == 'scored' else clean_text(match_groups[2])
            else:
                at = 'not-available'

            move = create_player_observation(
                player=player,
                event_type='advanced' if move_type in ['to', 'scored', 'safe at'] else 'out',
                at=at
            )

            is_bad_name = sum(
                1 if chunk in Positions else 0 for chunk in player.split(' ')
            )

            if is_bad_name > 0:
                print(f'possible bad name - "{player}" - {is_bad_name} bad chunk(s) found.')
                move['qaulity'] = 'bad'

            moves.append(move)

    return moves

def split_extras(extras: List[str]) -> Tuple[List[str], List[Dict[str, Any]]]:
    orders: List[str] = []
    moves: List[str] = []

    for extra in extras:
        extra = replace(
            [
                (r" on ((?:throwing|fielding| )*error|runner's fielder's choice|a balk).*$", ''),
                (r" in rundown.*$", ''),
            ],
            extra,
        )

        extra_split = [
            text.strip()
            for text
            in map(clean_text, re.split(r' ?to ', extra))
        ]

        if len(extra_split) > 1:
            has_positions = True
            for subset in extra_split:
                if len(subset) > 0:
                    has_positions = has_positions \
                        and any(token in Positions for token in subset.split(' '))

            if has_positions:
                orders.extend(subset for subset in extra_split if len(subset) > 0)
                continue

        moves.append(extra)

    return orders, handle_moves(moves)

def handle_extras(groups: List[str]) -> Dict[str, Any]:
    entities: Dict[str, Any] = {}

    orders, moves = split_extras(groups)
    if len(orders) > 0:
        entities['order'] = orders

    if len(moves) > 0:
        entities['moves'] = moves

    return entities
