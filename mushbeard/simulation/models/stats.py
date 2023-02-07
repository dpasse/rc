from typing import List
import math


class PlayerStats():
    def __init__(self, key: str, data: dict, likelihood_keys: List[str]) -> None:
        self.__key = key
        self.__data = data.copy()
        self.__likelihood_keys = likelihood_keys.copy()

    @property
    def key(self) -> str:
        return self.__key

    def likelihoods(self) -> dict:
        likelihood = {}
        for key in self.__likelihood_keys:
            likelihood[key] = self.__data[key] / self.__data['PA']

        return likelihood

class PitcherStats(PlayerStats):
    def __init__(self, key: str, data: dict):
        super().__init__(key, data, [])

class BatterStats(PlayerStats):
    def __init__(self, key: str, data: dict, probability_of_hitting: float = 1):
        given_data = data.copy()

        assert 'PA' in given_data or 'AB' in given_data
        for column in ('SH', 'SF', 'K', 'BB', 'HBP', '1B', '2B', '3B', 'HR'):
            assert column in given_data

        if not 'PA' in given_data:
            given_data['PA'] = sum(
                given_data[column] for column in ('BB', 'HBP', 'AB', 'SH', 'SF')
            )

        given_data['HITS'] = sum(
            given_data[column] for column in ('1B', '2B', '3B', 'HR')
        )

        given_data['E'] = math.floor(.018 * given_data['PA'])
        given_data['AtBats'] = sum(
            given_data[column] for column in ('AB', 'SF', 'SH')
        )
        given_data['Outs'] = given_data['AtBats'] - \
            sum(given_data[column] for column in ('HITS', 'E', 'K'))

        super().__init__(key, given_data, [
            'E',
            'Outs',
            'K',
            'BB',
            'HBP',
            '1B',
            '2B',
            '3B',
            'HR'
        ])

        self.__probability = probability_of_hitting

    @property
    def probability(self) -> float:
        return self.__probability
