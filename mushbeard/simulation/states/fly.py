from .typing import BasesType


def handle_medium_fly(bases: BasesType) -> BasesType:
    return bases[:2] + [0] + bases[2:]

def handle_long_fly(bases: BasesType) -> BasesType:
    return bases[:1] + [0] + bases[1:]
