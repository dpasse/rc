from .typing import BasesType


def handle_triple(bases: BasesType) -> BasesType:
    return [0, 0, 1] + bases
