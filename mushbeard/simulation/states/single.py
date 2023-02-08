from .typing import BasesType


def handle_single(bases: BasesType) -> BasesType:
    return [1] + bases

def handle_medium_single(bases: BasesType) -> BasesType:
    return handle_single(bases[:1] + [0] + bases[1:])

def handle_long_single(bases: BasesType) -> BasesType:
    return handle_single([0] + bases)
