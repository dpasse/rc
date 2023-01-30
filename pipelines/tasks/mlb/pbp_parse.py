from typing import List, Dict, Any

import os
import re
import json
import pandas as pd

from prefect import flow, task

from common.parsers.bbr.engines import PlayByPlayParser
from common.parsers.typing import HandleType


class PlayByPlayCsvToJsonConverter():
    def __init__(self, game_id: str) -> None:
        self.__game_id = game_id
        self.__input_path = f'../data/mlb/pbp/1/pbp_{self.__game_id}.csv'
        self.__output_path = f'../data/mlb/pbp/2/pbp_{self.__game_id}.json'
        self.__parser = PlayByPlayParser()

    def _convert(self) -> HandleType:
        df = pd.read_csv(self.__input_path, index_col=None)
        df['R/O'] = df['R/O'].astype(str)

        return {
            'id': self.__game_id,
            'periods': self.__parser.parse(df)
        }

    def _dump(self, game: Dict[str, Any]) -> None:
        with open(self.__output_path, 'w', encoding='UTF8') as output_file:
            json.dump(game, output_file, indent=4)

    def convert_and_dump(self) -> None:
        self._dump(self._convert())

##@task(timeout_seconds=5)
def get_pbp_rows(game_id: str) -> None:
    PlayByPlayCsvToJsonConverter(game_id).convert_and_dump()

@flow(name='mlb-pbp-parse')
def get_pbps(game_ids: List[str]) -> None:
    for game_id in game_ids:
        get_pbp_rows(game_id)

if __name__ == '__main__':
    get_pbps([
        re.sub(r'^pbp_|\.csv$', '', file)
        for file
        in os.listdir('../data/mlb/pbp/1/')
    ])
