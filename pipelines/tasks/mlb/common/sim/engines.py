import random
from typing import List, Tuple
from .models import AbstractBatters, EventVariable, EventCodes
from .state import Inning


class InningSimulator():
    def __init__(self, batters: AbstractBatters):
        self.__batters = batters

    def play(self):
        def generate_event(event_variables_with_ranges: List[Tuple[float, EventVariable]]) -> EventCodes:
            rand = random.random()
            for probability, event in event_variables_with_ranges:
                if rand <= probability:
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
