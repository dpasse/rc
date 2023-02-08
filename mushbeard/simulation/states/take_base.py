from .typing import BasesType


def handle_take_base(bases: BasesType) -> BasesType:
    if bases == [1, 1, 1]:
        return [1] + bases

    ## populate the first open base we encounter
    for i, has_runner in enumerate(bases):
        if has_runner == 0:
            bases[i] = 1
            break

    return bases
