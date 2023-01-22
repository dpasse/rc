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
    'left fielder',
    'right fielder',
    'center fielder',
])

StrikeOutEfforts = set([
    'swinging', 'looking', 'called out', 'bunting foul'
])

EventTypes = set([
    'inside-the-park-home run',
    "runner's fielder's choice",
    "grounded into fielder's choice",
    "hit into fielder's choice",
    "bunted into fielder's choice",
    'grounded into double play',
    "sacrificed into double play",
    'grounded into triple play',
    "fielder's indifference",
    'bunt popped into double play',
    'popped into double play',
    'popped into triple play',
    'flied into triple play',
    'bunt double',
    'bunt single',
    'dropped foul ball',
    'flied into double play',
    'lined into double play',
    'lined into triple play',
    "catcher's interference",
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
    'passed ball',
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
    'pitches',
    'walked',
    'sub-p',
    'sub-f',
    'stole',
    'error',
    'balk',
    'lined',
    'out'
])

Locations = set([
    'shallow right center',
    'shallow left center',
    'deep right center',
    'deep left center',
    'shallow center',
    'designated hitter',
    'shallow right',
    'right center',
    'shallow left',
    'left field',
    'shortstop first',
    'right field',
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
    'short',
    'shift',
    'left',
    'home',
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
    text = re.sub(r' safe at (first|second|third) and advances ', ' ', text)
    text = re.sub(r', ((?:[A-Z.]+ |)[A-Z][\w.-]+(?: [A-Za-z.]{2,3}|)) and ([A-Z]\w+) scored', r', \g<1> scored and \g<2> scored', text)


    return [
        text
        for text in map(
            clean_text,
            re.split(delimiter, text)
        )
        if len(text) > 0
    ]

def handle_moves(groups: List[str]) -> List[Dict[str, Any]]:
    def get_additional_information(text: str):
        additional_information_match = search(
            [
                r"( on (fielder's indifference|runner's fielder's choice|interference)(.*$))",
                r"( on(?: |a)+((?:throwing|fielding| )*error|wild pitch|passed ball|pickoff error|missed catch error)(.*$))",
                r"( on a (balk)(.*$))",
                r"( in (rundown)(.*$))",
                r"( (hit by batted ball))",
            ],
            text,
        )

        if additional_information_match:
            additional_information_groups = additional_information_match.groups()

            text = text.replace(additional_information_groups[0], '')

            how = {
                'how': additional_information_groups[1]
            }

            if len(additional_information_groups) > 2:
                by_information_match = search(
                    [
                        r"by (.+? (?:baseman|fielder)) (.+)",
                        r"by (shortstop|pitcher|catcher) (.+)",
                        r"by (.+)",
                    ],
                    additional_information_groups[2],
                )

                if by_information_match:
                    by_information_match_groups = by_information_match.groups()
                    by = by_information_match_groups[0] if len(by_information_match_groups) == 1 else by_information_match_groups[1]
                    if not by in Positions:
                        how['by'] = by

            return text, how

        additional_information_match = search(
            [
                r"( on (.+?) (wild pitch)\.?$)",
            ],
            text,
        )

        if additional_information_match:
            additional_information_groups = additional_information_match.groups()

            text = text.replace(additional_information_groups[0], '')

            by = additional_information_groups[1]
            if by in Positions:
                how = {
                    'how': additional_information_groups[2]
                }
            else:
                how = {
                    'how': additional_information_groups[2],
                    'by': additional_information_groups[1]
                }

            return text, how

        return text, None

    moves: List[Dict[str, Any]] = []
    for item in groups:
        text = item[:].strip()
        text = re.sub(r'^([A-Z][\w-]+) (first|second|third)(?=\.|$)', r'\g<1> to \g<2>', text)

        text, how = get_additional_information(text)

        advanced = ['to', 'scored', 'safe', 'stole', 'advanced to', 'walked', 'safe to']
        match = search([
                r'^ *(.+?) (out|out stretching|thrown out|safe) at (.+)',
                r'^ *(.+?) ((?:doubled|picked) off|caught stealing|to|safe to|stole|advanced to) (.+)',
                r'^ *(.+?) (thrown out|scored|walked|struck out)',
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
                event_type='advanced' if move_type in advanced else 'out',
                at=at
            )

            if how:
                move.update(how)

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
