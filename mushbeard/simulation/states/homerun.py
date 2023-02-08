from .typing import BasesType


def handle_homerun(bases: BasesType) -> BasesType:
    return [0, 0, 0, 1] + bases
