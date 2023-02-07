from typing import List, Optional, Tuple
import re
from dataclasses import dataclass

from .typing import OptionalHandleType, MatchType, HandlerType, ParserType


class Phrase():
    def __init__(self, text: str):
        self.__text = text

    @property
    def text(self) -> str:
        return self.__text

    def partition(self) -> Tuple[str, List[str]]:
        subsets = self.split()
        return subsets[0], subsets[1:] if len(subsets) > 1 else []

    def split(self) -> List[str]:
        return self.text.split(';')

class PlayByPlayDescriptionParser():
    def __init__(self, parsers: List[ParserType]) -> None:
        self.__parsers = parsers

    def __parse_text(self, text: str) -> OptionalHandleType:
        for parser in self.__parsers:
            observation = parser(text)
            if observation:
                return observation

        return None

    def parse(self, phrase: Phrase) -> OptionalHandleType:
        main_phrase, move_phrases = phrase.partition()
        observation = self.__parse_text(main_phrase)
        if observation is None:
            return None

        moves = [
            self.__parse_text(sub) for sub in move_phrases
        ]

        if len(moves) > 0:
            observation['moves'] = moves

        return observation

def create_play_by_play_description_parser(parsers: List[ParserType]) -> PlayByPlayDescriptionParser:
    return PlayByPlayDescriptionParser(parsers)

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
