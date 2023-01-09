import os
import sys
import time
import requests
import pandas as pd
from typing import List, cast

from bs4 import BeautifulSoup
from prefect import flow, task

from common.helpers.transformers import run, team, pythagorean


@task(retries=3)
def get_standing(season: str) -> List[dict]:
    response = requests.get(f'https://www.espn.com/mlb/standings/_/season/{season}')
    assert response.status_code == requests.status_codes.codes['ok']

    bs = BeautifulSoup(response.content, features='html.parser')
    tables = bs.select('.standings__table')
    if len(tables) == 0:
        raise KeyError('no .standings__table elements found')

    teams = []
    stats = []
    for table in tables:
        rows = table.select('tbody.Table__TBODY')

        for row in rows[0].select('tr'):
            if 'subgroup-headers' in row.attrs['class']:
                continue

            abbr = row.select_one('td .AnchorLink abbr')
            if abbr:
                teams.append(abbr.attrs['title'])

        headers = []
        for row in rows[1].select('tr'):
            if 'subgroup-headers' in row.attrs['class']:
                headers = [item.text for item in row.select('td')]
            else:
                record = dict(zip(headers, [item.text for item in row.select('td')]))
                record['season'] = season

                stats.append(record)

    data = []
    standings = dict(zip(teams, stats))
    for key, values in standings.items():
        record = { 'team': key }
        record.update(values)

        data.append(record)

    return data

@flow(name='mlb-standings', persist_result=False)
def get_standings(seasons: List[str]) -> None:
    def run_pythagorean(df: pd.DataFrame) -> pd.DataFrame:
      df = pythagorean(df, 2)
      df = pythagorean(df, 1.83)

      return df

    data: List[dict] = []
    for season in seasons:
        data.extend(cast(List[dict], get_standing(season)))

        time.sleep(8)

    df = run(
        pd.DataFrame(data),
        [team, run_pythagorean]
    )

    path = '../data/mlb/standings.csv'
    if os.path.exists(path):
        df_current = pd.read_csv(path)
        df_current['season'] = df_current['season'].astype(str)

        df_current = df_current[~df_current.season.isin(seasons)]
        if not df_current.empty:
            df = pd.concat([df, df_current])

    df.sort_values(['season']).to_csv(path, index=False)


if __name__ == '__main__':
    get_standings(sys.argv[1:])
