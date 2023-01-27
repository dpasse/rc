from typing import List, Tuple, cast

import sys
import os
import re
import time
import logging
import unidecode
import pandas as pd

from bs4 import Tag
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner

from common.helpers.web import make_request


Logger = logging.getLogger(__name__)
Logger.setLevel(level=logging.INFO)
Logger.addHandler(
    logging.FileHandler('../data/mlb/logs/schedule.log')
)

def extract_game(column: Tag) -> Tuple[str, str]:
    anchor = column.select_one('a')
    if anchor:
        match = re.search(
            r'\/([a-z]+)(\d+).shtml',
            anchor.attrs['href'],
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1), match.group(2)

    return '', ''

def extract_pitcher(column: Tag) -> str:
    anchor = column.select_one('a')
    if anchor:
        return unidecode.unidecode(anchor.attrs['title'])

    return ''

@task(retries=1, retry_delay_seconds=15)
def get_team_schedule(season: str, team: str) -> None:
    uri = f'../data/mlb/schedules/{team}_{season}.csv'
    if os.path.exists(uri):
        print('skipping...', season, team)
        return

    bs = make_request(
        f'https://www.baseball-reference.com/teams/{team}/{season}-schedule-scores.shtml',
    )

    div = bs.select_one('#team_schedule')
    if not div:
        return None

    collection = []
    for row in div.select('tbody tr'):
        if 'class' in row.attrs and 'thead' in row.attrs['class']:
            continue

        columns: List[Tag] = cast(List[Tag], list(row.children))

        headers = [
            col.attrs['data-stat'] for col in columns
        ]

        data = dict(zip(
            headers,
            [item.text for item in columns]
        ))

        del data['boxscore']

        data['date_game'] = columns[1].attrs['csk']

        team, game = extract_game(columns[2])
        data['team'] = team
        data['game'] = game

        data['winning_pitcher'] = extract_pitcher(columns[13])
        data['losing_pitcher'] = extract_pitcher(columns[14])
        data['saving_pitcher'] = extract_pitcher(columns[15])

        collection.append(data)

    pd.DataFrame(collection).to_csv(uri, index=None)

@task()
def sleep(timeout: int) -> None:
    print('sleeping...', timeout)
    time.sleep(timeout)

@flow(name='mlb-team-schedules', task_runner=SequentialTaskRunner())
def get_schedules(requests: List[Tuple[str, str]], timeout=15) -> None:
    for i, request in enumerate(requests):
        get_team_schedule.submit(*request)
        if i < (len(requests) - 1):
            sleep.submit(timeout)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        raise Exception('Need to provide options.')

    requests = []
    if args[0] == '-l':
        for _, row in pd.read_csv(args[1], index_col=None).iterrows():
            requests.append(
                (row['season'], row['team'])
            )

    if len(requests) > 0:
        get_schedules(requests)
