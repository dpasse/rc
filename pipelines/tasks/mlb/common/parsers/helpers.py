from typing import List, Callable, Optional
import re


def grab(match: re.Match, index: int) -> str:
    return match.group(index).strip()

class FindMatch():
    def __init__(self, expressions: List[str], handle_match: Callable[[Optional[re.Match[str]]], dict], flags: int = 0) -> None:
        self.__expressions = expressions
        self.__handle = handle_match
        self.__flags = flags

    def find(self, text: str) -> Optional[re.Match[str]]:
        match: Optional[re.Match[str]] = None
        for expression in self.__expressions:
            match = re.search(expression, text, flags=self.__flags)
            if match:
                break

        return match

    def parse(self, text: str) -> Optional[dict]:
        match = self.find(text)
        return self.__handle(match) if match else None

def create_find_match_request(expressions: List[str],  handle_match: Callable[[Optional[re.Match[str]]], dict], flags: int = 0) -> FindMatch:
    return FindMatch(expressions, handle_match, flags)

def parse_many(requests: List[FindMatch], text: str) -> dict:
    match: Optional[re.Match[str]] = None

    for request in requests:
        match = request.parse(text)
        if match:
            break

    return match
