from typing import List, Callable, Any, Optional, Dict
from .in_play import handle_in_play_outs, \
                     handle_in_play, \
                     handle_fielders_choice, \
                     handle_out_of_play_outs, \
                     handle_reached_on
from .strikeout import handle_strikeout
from .multiple_outs import handle_multiple_outs
from .wild_pitch import handle_wild_pitch
from .steal import handle_steal
from .error import handle_error
from .pick_off import handle_pick_off

play_by_play_parsers: List[Callable[[str], Optional[Dict[str, Any]]]] = [
    handle_wild_pitch,
    handle_pick_off,
    handle_steal,
    handle_strikeout,
    handle_multiple_outs,
    handle_out_of_play_outs,
    handle_in_play_outs,
    handle_reached_on,
    handle_fielders_choice,
    handle_in_play,
    handle_error,
]
