import os
import json
from prefect import flow, task

from common.helpers.parsers import parse_game


PBP_DIRECTORY = '../data/mlb/pbp/'

@task(retries=1, retry_delay_seconds=15)
def reparse(file: str) -> None:
    print(file)

    file_path = os.path.join(PBP_DIRECTORY, file)
    with open(file_path, 'r', encoding='UTF8') as pbp:
        game = json.loads(pbp.read())

    game = parse_game(game)

    if not game is None:
        with open(file_path, 'w', encoding='UTF8') as pbp:
            json.dump(game, pbp, indent=2)

@flow(name='mlb-reparse-pbp', persist_result=False)
def rerun_pbps() -> None:
    for file in os.listdir(PBP_DIRECTORY):
        reparse(file)


if __name__ == '__main__':
    rerun_pbps()
