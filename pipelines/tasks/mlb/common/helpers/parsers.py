import re
from typing import Optional, Tuple, Dict, Any, List, Callable


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

def split_extras(extras: List[str]) -> Tuple[List[str], List[Dict[str, Any]]]:
    orders, moves = [], []
    for extra in extras:
        extra = re.sub(r" (on ((?:throwing|fielding| )*error|runner's fielder's choice)|in rundown).*$", '', extra)

        extra_split = [
            text
            for text
            in map(clean_text, re.split(r' to ', extra))
            if len(text) > 0
        ]

        if len(extra_split) > 1:
            has_positions = True
            for subset in extra_split:
                has_positions = has_positions \
                    and any(token in Positions for token in subset.split(' '))

            if has_positions:
                orders.extend(extra_split)
                continue

        moves.append(extra)

    return orders, handle_moves(moves)

def handle_moves(groups: List[str]) -> List[Dict[str, Any]]:
    move_expressions = [
      r'^ *(.+?) (thrown out at|out(?: |stretching)+at|doubled off|caught stealing|safe at|to) (.+)',
      r'^ *(.+?) (thrown out|scored)',
    ]

    moves: List[Dict[str, Any]] = []
    for item in groups:
        match = None
        for expression in move_expressions:
            match = re.search(expression, item)
            if match:
                match_groups = match.groups()

                player = match_groups[0]
                move_type = match_groups[1]
                move = {
                    'player': player,
                    'type': 'advanced' if move_type in ['to', 'scored', 'safe at'] else 'out'
                }

                if move_type == 'scored' or len(match_groups) == 3:
                    move['at'] = 'home' if move_type == 'scored' else clean_text(match_groups[2])
                else:
                    move['at'] = 'not-available'

                is_bad_name = sum(
                    1 if chunk in Positions else 0 for chunk in player.split(' ')
                )

                if is_bad_name > 0:
                    print(f'possible bad name - "{player}" - {is_bad_name} bad chunk(s) found.')
                    move['qaulity'] = 'bad'

                moves.append(move)

                break

    return moves

def handle_outs_plus_moves(groups: List[str]) -> Dict[str, Any]:
    orders, moves = split_extras(groups)

    observation: Dict[str, Any] = {
        'order': orders,
    }

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_steals(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_in_play(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_in_play_out(groups: List[str]) -> Dict[str, Any]:
    observation = {
        'outs': 1,
    }

    observation.update(handle_in_play(groups))
    return observation

def handle_strike_outs(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation = {
        'player': groups[0],
        'type': groups[1],
        'effort': extras[0],
        'outs': 1,
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_homerun(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(
        re.sub(r'\([^)]+\)', '', groups[2]),
        r'(,| and )'
    )

    observation = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'runs': 1,
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_walk(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[1])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': extras[0],
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_subs(groups: List[str]) -> Dict[str, Any]:
    return {
        'player': groups[0],
        'type': 'sub-p' if clean_text(groups[1]).startswith('pitch') else 'sub-f',
    }

def handle_multiple_outs(groups: List[str]) -> Dict[str, Any]:
    observation_type = clean_text(groups[1].lower())
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': observation_type,
        'outs': 1,
    }

    observation.update(
        handle_outs_plus_moves(split_text(groups[2]))
    )

    return observation

def handle_caught_stealing(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'outs': 1,
    }

    observation.update(
        handle_outs_plus_moves(extras[1:])
    )

    return observation

def handle_fielders_choice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0]
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

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

def handle_error(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': groups[1],
    }

    orders, moves = split_extras(
        split_text(groups[0])
    )

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_sacrifice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'outs': 1,
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_attempted_sacrifice(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1]
    }

    extras = split_text(groups[2])
    orders, moves = split_extras(extras)

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

def handle_balk(groups: List[str]) -> Dict[str, Any]:
    extras = re.sub(r'on a balk', '', groups[0]).split(',')
    observation: Dict[str, Any] = {
        'type': 'balk',
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

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

def handle_catcher_interference(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': extras[0],
        'at': groups[1],
    }

    orders, moves = split_extras(extras[1:])

    if len(orders) > 0:
        observation['order'] = orders

    if len(moves) > 0:
        observation['moves'] = moves

    return observation

class EventDescriptionParser():
    def __init__(self) -> None:
        self.__parse_event_expressions: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
            (r'^(.+?) (struck out) (.+)', handle_strike_outs),
            (r'^(.+? (?:balk).+)', handle_balk),
            (r'^(.+?) to (.+?) on (pickoff error) by (?:pitcher|catcher) (.+)', handle_pick_off_error),
            (r'^(.+?) (picked off) and caught stealing (.+)', handle_pick_off),
            (r'^(.+?) (picked off) (.+)', handle_pick_off),
            (r'^(.+?) ((?:homer)ed) to (.+)', handle_homerun),
            (r'^(.+? (?:wild pitch|passed ball).+)', handle_wild_pitch),
            (r'^(.+?) ((?:(?:intentionally |)walked|hit by pitch).*)', handle_walk),
            (r'^(.+?)(?: |hit a)+((?:singl|doubl|tripl)ed|ground rule double) to (.+)', handle_in_play),
            (r'^(.+?) reached on (infield single|bunt single) to (.+)', handle_in_play),
            (r'^(.+?) reached (.+?)(?: |base)+on (catcher\'s interference.+)', handle_catcher_interference),
            (r'^(.+?)(?: |bunt)+((?:lin|ground|fli|foul|popp)ed out) to (.+)', handle_in_play_out),
            (r'^(.+?) ((?:ground|lin|fli|popp)ed into (?:double|triple) play)(.+)', handle_multiple_outs),
            (r'^(.+?) ((?:ground|lin|fli)ed into fielder\'s choice) to (.+)', handle_fielders_choice),
            (r'^(.+?) (sacrificed),(.+)', handle_attempted_sacrifice),
            (r'^(.+?)(?: |hit)+(sacrifice fly|sacrificed) to (.+)', handle_sacrifice),
            (r'^(.+?) (caught stealing) (.+)', handle_caught_stealing),
            (r'^(.+?) (stole) (.+)', handle_steals),
            (r'(.+on ((?:fielding|throwing) error).+)', handle_error),
            (r'^(.+?) ((?:hit|ran) for|in\b|a[st]\b|catching|pitch(?:ing|es to))', handle_subs),
        ]

    def transform_into_object(self, description: str) -> Optional[dict]:
        description_as_object = None
        for expression, mapping_function in self.__parse_event_expressions:
            match = re.search(expression, description)
            if match:
                description_as_object = mapping_function(list(match.groups()))

                for key in ['type', 'at', 'by']:
                    if key in description_as_object:
                        description_as_object[key] = clean_text(description_as_object[key])

                        if key in ['type', 'at']:
                            description_as_object[key] = description_as_object[key].lower()

                if 'moves' in description_as_object:
                    outs = sum(
                        1
                        for move
                        in description_as_object['moves']
                        if move['type'] == 'out'
                    )

                    if outs > 0:
                        if not 'outs' in description_as_object:
                            description_as_object['outs'] = 0

                        description_as_object['outs'] += outs

                    runs = sum(
                        1
                        for move
                        in description_as_object['moves']
                        if move['at'] == 'home' and move['type'] != 'out'
                    )

                    if runs > 0:
                        if not 'runs' in description_as_object:
                            description_as_object['runs'] = 0

                        description_as_object['runs'] += runs

                break

        return description_as_object
