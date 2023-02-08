from .event_codes import EventCodes


class EventVariable():
    def __init__(self, event_code: EventCodes = EventCodes.ParentEvent, probability: float = 1):
        self.__event_code = event_code
        self.__probability = probability

    @property
    def event_code(self) -> EventCodes:
        return self.__event_code

    @property
    def probability(self) -> float:
        return self.__probability

    def __repr__(self):
        event_name = 'EMPTY' if self.event_code is None else self.event_code.name
        return f'<EventVariable name="{event_name}" probability="{self.probability}">'
