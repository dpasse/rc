from typing import List

from .helpers import FindMatch
from .in_play import handle_in_play_outs, \
                     handle_in_play, \
                     handle_fielders_choice, \
                     handle_out_of_play_outs, \
                     handle_reached_on, \
                     handle_ground_rule_double
from .strikeout import handle_strikeout
from .multiple_outs import handle_multiple_outs
from .wild_pitch import handle_wild_pitch, handle_passed_ball
from .steal import handle_steal, handle_caught_stealing
from .error import handle_error
from .pick_off import handle_pick_off
from .advance import handle_advance, handle_out_advance
from .balk import handle_balk
from .interference import handle_interference

def create_default_play_by_play_parsers_list() -> List[FindMatch]:
    return [
        handle_passed_ball(),
        handle_wild_pitch(),
        handle_pick_off(),
        handle_caught_stealing(),
        handle_steal(),
        handle_strikeout(),
        handle_multiple_outs(),
        handle_out_of_play_outs(),
        handle_in_play_outs(),
        handle_reached_on(),
        handle_fielders_choice(),
        handle_ground_rule_double(),
        handle_in_play(),
        handle_error(),
        handle_balk(),
        handle_out_advance(),
        handle_advance(),
        handle_interference(),
    ]
