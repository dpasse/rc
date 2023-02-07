from .typing import BASES_TYPE


def handle_homerun(bases: BASES_TYPE) -> BASES_TYPE:
    return [0, 0, 0, 1] + bases
