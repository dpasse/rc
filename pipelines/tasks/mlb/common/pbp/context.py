from dataclasses import dataclass
from .models import Entities
from typing import List, Optional
import unidecode


@dataclass
class OnBase():
    player: str
    at: str

@dataclass
class BasesState():
    before: List[int]
    after: List[int]

class BasesContext():

    def __init__(self) -> None:
        self.__lookup = {
            'first': 0,
            'second': 1,
            'third': 2,
            'home': 3,
        }

        self.__reverse_lookup = {
            0: 'first',
            1: 'second',
            2: 'third',
            3: 'home',
        }

        self.__on_base: List[OnBase] = []

    def clean_player_name(player) -> str:
        return unidecode.unidecode(player)

    def remove(self, player: str) -> None:
        player = BasesContext.clean_player_name(player)

        self.__on_base = [
            item
            for item in self.__on_base
            if item.player != player
        ]

    def get(self, player: str) -> Optional[OnBase]:
        player = BasesContext.clean_player_name(player)

        found = [
            item
            for item in self.__on_base
            if item.player == player
        ]

        if len(found) == 1:
            return found[0]

        return None

    def add(self, player: str, at: str) -> None:
        player = BasesContext.clean_player_name(player)

        found = self.get(player)
        if found:
            assert self.__lookup[at] >= self.__lookup[found.at], found

        self.remove(player)

        if at != 'home':
            self.__on_base.append(OnBase(player, at))

    def switch(self, player: str, for_player: str) -> None:
        for_player = BasesContext.clean_player_name(for_player)

        found = self.get(for_player)
        if found:
            self.remove(for_player)
            self.add(player, found.at)

    def play(self, entities: Entities) -> BasesState:
        before = self.to_list()

        if entities.type in ['sub-f']:
            if 'for' in entities.body:
                self.switch(entities.body['player'], entities.body['for'])

        if entities.type in ['balk']:
            for on_base in self.__on_base:
                self.add(on_base.player, self.__reverse_lookup[self.__lookup[on_base.at] + 1])

        if "into fielder's choice" in entities.type:
            self.add(entities.body['player'], 'first')

        if entities.type in ['singled', 'infield single', 'hit by pitch', 'walked', 'intentionally walked', 'bunt single']:
            self.add(entities.body['player'], 'first')

        if entities.type in ['doubled', 'doubles', 'ground rule double', 'bunt double']:
            self.add(entities.body['player'], 'second')

        if entities.type in ['tripled', 'triples']:
            self.add(entities.body['player'], 'third')

        for move in entities.moves:
            if move.type == 'advanced':
                assert self.get(move.body['player']) ## events are out of order
                self.add(move.body['player'], move.at)

            if move.type == 'out':
                assert self.get(move.body['player']) ## events are out of order
                self.remove(move.body['player'])

        if entities.type in ['homered', 'inside-the-park-home run']:
            self.__on_base.clear()

        self.validate()

        return BasesState(
            before,
            self.to_list()
        )

    def validate(self):
        assert not len(self.__on_base) > 3

        bases = [0, 0, 0]
        for item in self.__on_base:
            assert bases[self.__lookup[item.at]] != 1
            bases[self.__lookup[item.at]] = 1

    def to_list(self):
        bases = [0, 0, 0]
        for item in self.__on_base:
            bases[self.__lookup[item.at]] = 1

        return bases
