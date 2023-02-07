from typing import List

from ..typing import ParserType
from .in_play import parse_single, \
                     parse_double, \
                     parse_triple, \
                     parse_homerun, \
                     parse_walk, \
                     parse_hit_by_pitch, \
                     parse_fielders_choice, \
                     parse_lineout, \
                     parse_flyball, \
                     parse_popfly, \
                     parse_groundout, \
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
from .indifference import parse_indifference


_parsers = [
    parse_passed_ball(),
    parse_wild_pitch(),
    parse_pick_off(),
    parse_caught_stealing(),
    parse_steal(),
    parse_strikeout(),
    parse_multiple_outs(),
    parse_lineout(),
    parse_flyball(),
    parse_popfly(),
    parse_groundout(),
    parse_reached_on(),
    parse_fielders_choice(),
    parse_ground_rule_double(),
    parse_single(),
    parse_double(),
    parse_triple(),
    parse_homerun(),
    parse_walk(),
    parse_hit_by_pitch(),
    parse_error(),
    parse_balk(),
    parse_out_advance(),
    parse_advance(),
    parse_interference(),
    parse_indifference(),
]

def get_parsers() -> List[ParserType]:
    return _parsers
