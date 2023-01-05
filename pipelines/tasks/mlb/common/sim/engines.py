import random
from .state import Inning


class InningSimulator():
    def __init__(self, batters):
        self.__batters = batters

    def play(self):
        def generate_event(event_variables_with_ranges):
            rv = random.random()
            for p, ev in event_variables_with_ranges:
                if rv <= p:
                    return ev.event_code


            raise ValueError('No Event Code was generated!')

        inning = Inning()
        while not inning.is_over():
            event_variables, _ = self.__batters.next()

            inning.execute(
                generate_event(event_variables),
            )

        return inning.history
