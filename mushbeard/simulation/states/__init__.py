from typing import Callable, Dict

from .typing import BASES_TYPE
from .error import handle_error
from .take_base import handle_take_base
from .single import handle_single, handle_medium_single, handle_long_single
from .double import handle_double, handle_long_double
from .triple import handle_triple
from .homerun import handle_homerun
from .ground_ball import handle_ground_into_double_play, handle_normal_ground_ball
from .fly import handle_long_fly, handle_medium_fly
from ..models import EventCodes


STATE_LOOKUP_TYPE = Dict[EventCodes, Callable[[BASES_TYPE], BASES_TYPE]]

_states = {
    EventCodes.Error: handle_error,
    EventCodes.Walk: handle_take_base,
    EventCodes.HBP: handle_take_base,
    EventCodes.ShortSingle: handle_single,
    EventCodes.MediumSingle: handle_medium_single,
    EventCodes.LongSingle: handle_long_single,
    EventCodes.ShortDouble: handle_double,
    EventCodes.LongDouble: handle_long_double,
    EventCodes.Triple: handle_triple,
    EventCodes.HR: handle_homerun,
    EventCodes.GIDP: handle_ground_into_double_play,
    EventCodes.NormalGroundBall: handle_normal_ground_ball,
    EventCodes.MediumFly: handle_medium_fly,
    EventCodes.LongFly: handle_long_fly,
}

def get_states():
    return _states
