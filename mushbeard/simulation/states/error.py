from .typing import BASES_TYPE


def handle_error(bases: BASES_TYPE) -> BASES_TYPE:
    return [1] + bases
