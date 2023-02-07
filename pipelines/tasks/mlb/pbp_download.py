from typing import List, Optional, Tuple

import os
import sys
import re
import time
import unidecode
import pandas as pd

from bs4 import BeautifulSoup
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner


from find import root
sys.path.append(root())

from mushbeard.helpers.web import make_request


HEADERS = [
    'Inn',
    'Score',
    'Out',
    'RoB',
    'Pit(cnt)',
    'R/O',
    '@Bat',
    'Batter',
    'Pitcher',
    'wWPA',
    'wWE',
    'Play Description',
]

@task(name='mlb-download', retries=3, retry_delay_seconds=15, timeout_seconds=5)
def get_pbp(team: str, game: str) -> None:
    uri = f'../data/mlb/pbp/1/pbp_{game}.csv'
    if os.path.exists(uri):
        print('skipping...', game)
        return

    page = make_request(
        f'https://www.baseball-reference.com/boxes/{team}/{game}.shtml'
    )

    pbp_div = page.select_one('#all_play_by_play')
    if not pbp_div:
        return

    div_text = re.sub(r'(<!--|-->)', '', pbp_div.prettify())
    div = BeautifulSoup(div_text, features='html.parser')

    data: List[dict] = []
    for pbp in div.select('#div_play_by_play tbody tr'):
        observation: Optional[dict] = None

        if 'id' in pbp.attrs:
            observation = {
                'id': pbp.attrs['id']
            }

            observation.update(
                dict(zip(HEADERS, map(lambda a: a.text, pbp.children)))
            )
        elif 'class' in pbp.attrs:
            observation = {
                'Play Description': list(pbp.children)[-1].text
            }

            if 'pbp_summary_top' in pbp.attrs['class']:
                observation['Inn'] = 'e-start'

            if 'pbp_summary_bottom' in pbp.attrs['class']:
                observation['Inn'] = 'e-end'

        if observation:
            for key in ['Play Description', 'Batter', 'Pitcher', 'Pit(cnt)']:
                if key in observation:
                    observation[key] = unidecode.unidecode(observation[key])

            data.append(observation)

    df = pd.DataFrame(data).drop(columns=['wWPA', 'wWE'])
    df.Inn = df.Inn.bfill(axis = 0)
    df.to_csv(uri, index=False)

@task(name='mlb-sleep')
def sleep(timeout: int) -> None:
    time.sleep(timeout)

@flow(name='mlb-pbp', task_runner=SequentialTaskRunner())
def get_pbps(requests: List[Tuple[str, str]], timeout = 15) -> None:
    for i, request in enumerate(requests):
        get_pbp.submit(*request)
        if i < (len(requests) - 1):
            sleep.submit(timeout)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        raise Exception('Need to provide options.')

    games: List[Tuple[str, str]] = []

    if args[0] == '-l':
        games = []
        for _, row in pd.read_csv(args[1], index_col=None).iterrows():
            games.append(
                (row['team'], f'{row["team"]}{row["game"]}')
            )

    if len(games) > 0:
        get_pbps(games)
