from .typing import MatchType


def grab(match: MatchType, index: int) -> str:
    return match.group(index).strip()
