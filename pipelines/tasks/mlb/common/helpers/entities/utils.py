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

StrikeOutEfforts = set([
    'swinging', 'looking', 'called out'
])

EventTypes = set([
    'inside-the-park-home run',
    "runner's fielder's choice",
    "grounded into fielder's choice",
    'grounded into double play',
    "fielder's indifference",
    'popped into double play',
    'flied into double play',
    "catcher's interference",
    'lined into double play',
    'intentionally walked',
    'ground rule double',
    'caught stealing',
    'throwing error',
    'infield single',
    'fielding error',
    'pickoff error',
    'sacrifice fly',
    'hit by pitch',
    'grounded out',
    'bunt single',
    'wild pitch',
    'fouled out',
    'struck out',
    'picked off',
    'popped out',
    'sacrificed',
    'flied out',
    'lined out',
    'advanced',
    'homered',
    'doubled',
    'doubles',
    'tripled',
    'triples',
    'singled',
    'singles',
    'walked',
    'sub-p',
    'sub-f',
    'stole',
    'error',
    'balk',
    'out'
])

Locations = set([
    'shallow right center',
    'shallow left center',
    'deep right center',
    'deep left center',
    'shallow center',
    'shallow right',
    'right center',
    'shallow left',
    'deep center',
    'left center',
    'deep right',
    'deep left',
    'shortstop',
    'pitcher',
    'catcher',
    'second',
    'center',
    'third',
    'right',
    'first',
    'left',
    'home'
])


def create_player_observation(
    player: str,
    event_type: str,
    at: Optional[str] = None,
    outs: Optional[int] = None,
    runs: Optional[int] = None,
    extras: Optional[List[str]] = None):

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

def is_event_type(event_type: str) -> bool:
    return event_type in EventTypes

def is_location(location: str) -> bool:
    return location in Locations

def is_player(player: str) -> bool:
    for chunk in player.split(' '):
        if chunk[0].islower():
            return False

    return True

def is_position(position: str) -> bool:
    return position in Positions

def is_strike_out_effort(effort: str) -> bool:
    return effort in StrikeOutEfforts

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
        text = item[:]
        additional_information = search(
            [
                r"( on ((?:throwing|fielding| )*error|runner's fielder's choice|fielder's indifference|wild pitch).*$)",
                r"( on a (balk).*$)",
                r"( in (rundown).*$)",
                r"( (hit by batted ball))",
            ],
            text,
        )

        how = None
        if additional_information:
            text = text.replace(additional_information.group(1), '')
            how = additional_information.group(2)

        match = search([
                r'^ *(.+?) (out|out stretching|thrown out|safe) at (.+)',
                r'^ *(.+?) (doubled off|caught stealing|to|stole) (.+)',
                r'^ *(.+?) (thrown out|scored)',
            ],
            text,
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
                event_type='advanced' if move_type in ['to', 'scored', 'safe', 'stole'] else 'out',
                at=at
            )

            if how:
                move['how'] = how

            moves.append(move)

    return moves

def split_extras(extras: List[str]) -> Tuple[List[str], List[Dict[str, Any]]]:
    orders: List[str] = []
    moves: List[str] = []

    for extra in extras:
        text = extra[:]

        extra_split = [
            text.strip()
            for text
            in map(clean_text, re.split(r' ?to ', text))
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
