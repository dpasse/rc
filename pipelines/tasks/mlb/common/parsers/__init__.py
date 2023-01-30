from typing import List

from .typing import ParserType
from .in_play import parse_in_play_outs, \
                     parse_in_play, \
                     parse_fielders_choice, \
                     parse_out_of_play_outs, \
                     parse_reached_on, \
                     parse_ground_rule_double
from .strikeout import parse_strikeout
from .multiple_outs import parse_multiple_outs
from .wild_pitch import parse_wild_pitch, parse_passed_ball
from .steal import parse_steal, parse_caught_stealing
from .error import parse_error
from .pick_off import parse_pick_off
from .advance import parse_advance, parse_out_advance
from .balk import parse_balk
from .interference import parse_interference


def create_default_play_by_play_parsers_list() -> List[ParserType]:
    return [
        parse_passed_ball(),
        parse_wild_pitch(),
        parse_pick_off(),
        parse_caught_stealing(),
        parse_steal(),
        parse_strikeout(),
        parse_multiple_outs(),
        parse_out_of_play_outs(),
        parse_in_play_outs(),
        parse_reached_on(),
        parse_fielders_choice(),
        parse_ground_rule_double(),
        parse_in_play(),
        parse_error(),
        parse_balk(),
        parse_out_advance(),
        parse_advance(),
        parse_interference(),
    ]
