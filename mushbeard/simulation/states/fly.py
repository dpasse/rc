from .typing import BASES_TYPE


def handle_medium_fly(bases: BASES_TYPE) -> BASES_TYPE:
    return bases[:2] + [0] + bases[2:]

def handle_long_fly(bases: BASES_TYPE) -> BASES_TYPE:
    return bases[:1] + [0] + bases[1:]
