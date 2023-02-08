from .typing import BasesType


def handle_double(bases: BasesType) -> BasesType:
    return [0, 1] + bases

def handle_long_double(bases: BasesType) -> BasesType:
    return handle_double([0] + bases)
