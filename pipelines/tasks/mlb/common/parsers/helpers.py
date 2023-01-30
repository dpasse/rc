from typing import List, Callable, Optional, Dict, Any
import re
from dataclasses import dataclass

from .typing import OptionalHandleType


@dataclass(frozen=True)
class FindMatch():
    expressions: List[str]
    handle: Callable[[re.Match[str]], Dict[str, Any]]
    flags: int

    def find(self, text: str) -> Optional[re.Match[str]]:
        for expression in self.expressions:
            match = re.search(expression, text, flags=self.flags)
            if match:
                return match

        return None

    def parse(self, text: str) -> OptionalHandleType:
        match = self.find(text)
        return self.handle(match) if match else None

def create_find_match_request(expressions: List[str],  handle_match: Callable[[re.Match[str]], Dict[str, Any]], flags: int = 0) -> FindMatch:
    return FindMatch(expressions, handle_match, flags)

def grab(match: re.Match, index: int) -> str:
    return match.group(index).strip()
