from .typing import BASES_TYPE


def handle_single(bases: BASES_TYPE) -> BASES_TYPE:
    return [1] + bases

def handle_medium_single(bases: BASES_TYPE) -> BASES_TYPE:
    return handle_single(bases[:1] + [0] + bases[1:])

def handle_long_single(bases: BASES_TYPE) -> BASES_TYPE:
    return handle_single([0] + bases)
