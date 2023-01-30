from typing import List

import os
import re
import json
import pandas as pd

from prefect import flow, task

from common.parsers.engines import PlayByPlayParser


##@task(timeout_seconds=5)
def get_pbp_rows(game_id: str) -> None:
    df = pd.read_csv(f'../data/mlb/pbp/1/pbp_{game_id}.csv')
    df['R/O'] = df['R/O'].astype(str)

    game = {
        'id': game_id,
        'periods': PlayByPlayParser().parse(df)
    }

    with open(f'../data/mlb/pbp/2/pbp_{game_id}.json', 'w', encoding='UTF8') as output_file:
        json.dump(game, output_file, indent=4)

##@flow(name='mlb-pbp-parse')
def get_pbps(game_ids: List[str]) -> None:
    for game_id in game_ids:
        get_pbp_rows(game_id)

if __name__ == '__main__':
    get_pbps([
        re.sub(r'^pbp_|\.csv$', '', file)
        for file
        in os.listdir('../data/mlb/pbp/1/')
    ])
