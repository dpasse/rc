from .typing import BASES_TYPE


def handle_double(bases: BASES_TYPE) -> BASES_TYPE:
    return [0, 1] + bases

def handle_long_double(bases: BASES_TYPE) -> BASES_TYPE:
    return handle_double([0] + bases)
