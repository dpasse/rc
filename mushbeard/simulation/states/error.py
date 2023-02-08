from .typing import BasesType


def handle_error(bases: BasesType) -> BasesType:
    return [1] + bases
