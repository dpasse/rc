import random
from typing import List, Tuple
from .state import Inning

from .models import EventCodes, EventVariable, AbstractBatters, BatterStats


class InningSimulator():
    def __init__(self, batters: AbstractBatters):
        self.__batters = batters

    def play(self) -> Inning:
        def generate_event(event_variables_with_ranges: List[EventVariable]) -> EventCodes:
            rand = random.random()
            for event in event_variables_with_ranges:
                if rand <= event.probability:
                    return event.event_code

            raise ValueError('No Event Code was generated!')

        inning = Inning()
        while not inning.is_over():
            player, event_variables = self.__batters.next()

            inning.execute(
                player.key,
                generate_event(event_variables),
            )

        return inning
