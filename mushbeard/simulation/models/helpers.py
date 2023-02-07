from typing import TypeVar, List, Tuple

from .stats import BatterStats
from .event_variable import EventVariable


T = TypeVar('T', EventVariable, BatterStats)
def create_probability_ranges(events: List[T]) -> List[Tuple[float, T]]:
    threshold = 0.0
    ranges: List[Tuple[float, T]] = []
    for i, event in enumerate(events):
        threshold = 1 if len(events) - 1 == i else threshold + event.probability
        ranges.append((threshold, event))

    return ranges
