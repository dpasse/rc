from typing import List, cast
import pandas as pd
import numpy as np
from common.helpers.normalizers import TeamNormalizer
import os
import re
import requests
import time
from bs4 import BeautifulSoup
from prefect import flow, task
import sys


@task(retries=1)
def get_team_schedule(season: str, abbr: str, team: int) -> List[dict]:
    collection = []
    for half in [1, 2]:
        url = f'https://www.espn.com/mlb/team/schedule/_/name/{abbr}/season/2022/seasontype/2/half/{half}'
        print('running: ', url)

        response = requests.get(url)

        assert response.status_code == requests.status_codes.codes['ok']

        bs = BeautifulSoup(response.content, features='html.parser')

        schedules = [ card for card in bs.select('.Card') if len(card.select('.schedule__header')) > 0 ]
        for schedule in schedules:

            rows = schedule.select('.Table__TBODY tr')

            tds = rows[0].select('td')
            headers = ['TEAM', 'SEASON', 'HALF'] + [ column.text for column in tds ] + ['GAME_ID', 'DESC']
            n_headers = len(tds)

            for row in rows[1:]:

                columns = row.select('td')
                data = [column.text.strip() for column in columns]

                if len(data) ==  n_headers:
                    game_id = ''
                    anchor = columns[2].select_one('a.AnchorLink')
                    if anchor:
                        match = re.search(r'\/gameId\/(.+)$', anchor.attrs['href'])
                        if match:
                            game_id = match.groups()[0]

                    collection.append(dict(zip(headers, [team, season, half] + data + [game_id, ''])))
                else:
                    collection.append(dict(zip(headers, [team, season, half] + data[:2] + ([''] * 7) + data[2:])))

        if half == 1:
            time.sleep(5)

    return collection

@flow(name='mlb-team-schedules', persist_result=False)
def get_schedules(season: str, abbrs: List[str]) -> None:
    data: List[dict] = []

    teams = []
    team_normalizer = TeamNormalizer()
    for abbr in abbrs:
        team = team_normalizer.get(abbr)
        data.extend(cast(List[dict], get_team_schedule(season, abbr, team)))

        teams.append(team)

    df = pd.DataFrame(data)

    path = '../data/mlb/schedules.csv'
    if os.path.exists(path):
        df_current = pd.read_csv(path)
        df_current['TEAM'] = df_current['TEAM'].astype(int)
        df_current['SEASON'] = df_current['SEASON'].astype(str)

        df_current = df_current[~df_current.TEAM.isin(teams) & df_current.SEASON != season]
        print(df_current.TEAM.unique())
        if not df_current.empty:
            df = pd.concat([df, df_current])

    df.sort_values(['TEAM', 'SEASON', 'HALF']).to_csv(path, index=False)

if __name__ == '__main__':
    get_schedules(str(sys.argv[1]), sys.argv[2:])
