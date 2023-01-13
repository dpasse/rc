from typing import List, Dict, Optional, cast
import sys
import os
import re
import time
import logging
import datetime
import numpy as np
import pandas as pd

from bs4 import ResultSet, Tag
from prefect import flow, task

from common.helpers.normalizers import TeamNormalizer
from common.helpers.web import make_request
from common.helpers.merges import merge


Logger = logging.getLogger(__name__)
Logger.setLevel(level=logging.INFO)
Logger.addHandler(
    logging.FileHandler('../data/mlb/logs/schedule.log')
)

def extract_game(columns: ResultSet[Tag]) -> str:
    anchor = columns[2].select_one('a.AnchorLink')
    if anchor:
        match = re.search(r'\/gameId\/(.+)$', anchor.attrs['href'])
        if match:
            return match.group(1)

    return ''


@task(retries=1, retry_delay_seconds=15)
def get_team_schedule(season: str, abbr: str, team: int) -> List[dict]:
    collection = []
    for half in [1, 2]:
        bs = make_request(
            f'https://www.espn.com/mlb/team/schedule/_/name/{abbr}/season/2022/seasontype/2/half/{half}'
        )

        for schedule in (
            card
            for card in bs.select('.Card')
            if len(card.select('.schedule__header')) > 0
        ):
            rows = schedule.select('.Table__TBODY tr')

            tds = rows[0].select('td')
            for row in rows[1:]:
                columns = row.select('td')
                data = [column.text.strip() for column in columns]
                collection.append(
                    dict(zip(
                        ['TEAM', 'SEASON', 'HALF'] + [ column.text for column in tds ] + ['GAME_ID', 'DESC'],
                        [team, season, half] + data + [extract_game(columns), '']
                        if len(data) == len(tds)
                        else [team, season, half] + data[:2] + ([''] * 7) + data[2:],
                    ))
                )

        if half == 1:
            time.sleep(5)

    return collection

@flow(name='mlb-team-schedules', persist_result=False)
def get_schedules(season: str, abbrs: List[str]) -> None:
    data: List[dict] = []
    team_normalizer = TeamNormalizer()

    path = '../data/mlb/schedules.csv'
    df_current: Optional[pd.DataFrame] = None
    if os.path.exists(path):
        df_current = pd.read_csv(path)
        df_current['TEAM'] = df_current['TEAM'].astype(int)
        df_current['SEASON'] = df_current['SEASON'].astype(str)
        df_current['GAME_ID'] = df_current['GAME_ID'].astype(str)

    for abbr in abbrs:
        team = team_normalizer.get(abbr)
        data.extend(
            cast(List[dict], get_team_schedule(season, abbr, team))
        )

        ## remove entries from df_current
        if not df_current is None:
            df_current = df_current.loc[~np.logical_and(df_current.TEAM == team, df_current.SEASON == season)]

        time.sleep(8)

    df = pd.DataFrame(data)
    df['TEAM'] = df['TEAM'].astype(int)
    df['SEASON'] = df['SEASON'].astype(str)
    df['GAME_ID'] = df['GAME_ID'].astype(str)

    if not df_current is None:
        df = merge(df, df_current)
        df['TEAM'] = df['TEAM'].astype(int)
        df['SEASON'] = df['SEASON'].astype(str)
        df['GAME_ID'] = df['GAME_ID'].astype(str)

    df.sort_values(['TEAM', 'SEASON', 'HALF']).to_csv(path, index=False)



if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        raise Exception('Need to provide options.')

    input_data: Dict[str, List[str]] = {}

    if args[0] == '-l':
        FILE_PATH = args[1]
        df_input = pd.read_csv(FILE_PATH, index_col=None)
        df_input['season'] = df_input['season'].astype(str)
        df_input['team'] = df_input['team'].astype(str)

        input_data = df_input.groupby(['season'])['team'].apply(list).to_dict()
    else:
        input_data = {
            sys.argv[1]: sys.argv[2:]
        }

    Logger.info('Started @ %s', datetime.datetime.now())

    for input_season, input_teams in input_data.items():
        Logger.info('    - %s', input_season)
        Logger.info('    - #%s', len(input_teams))

        get_schedules(input_season, input_teams)

    Logger.info('Finished @ %s', datetime.datetime.now())
    Logger.info('')
