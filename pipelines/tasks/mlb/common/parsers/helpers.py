from abc import ABC, abstractmethod
from typing import List, Optional
import re
from dataclasses import dataclass

from .typing import OptionalHandleType, MatchType, HandlerType


@dataclass(frozen=True)
class FindMatch():
    expressions: List[str]
    handler: HandlerType
    flags: int

    def find(self, text: str) -> Optional[MatchType]:
        for expression in self.expressions:
            match = re.search(expression, text, flags=self.flags)
            if match:
                return match

        return None

    def parse(self, text: str) -> OptionalHandleType:
        match = self.find(text)
        return self.handler(match) if match else None

def create_find_match_request(expressions: List[str],  handle_match: HandlerType, flags: int = 0) -> FindMatch:
    return FindMatch(expressions, handle_match, flags)

def grab(match: MatchType, index: int) -> str:
    return match.group(index).strip()


class AbstrractPlayByPlayDescriptionParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> OptionalHandleType:
        pass
