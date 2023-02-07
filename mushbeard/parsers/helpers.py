import re
import unidecode

from .typing import MatchType


def clean_text(text: str) -> str:
    text = unidecode.unidecode(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

def grab_match_group(match: MatchType, index: int) -> str:
    if index > len(match.groups()):
        raise IndexError('Index out of range')

    return clean_text(match.group(index))
