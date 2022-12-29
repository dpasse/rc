from typing import List

import os
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from prefect import flow, task

from normalizer import TeamNormalizer


@task(retries=3)
def get_stats_by_season(season: str) -> List[dict]:
    response = requests.get(f'https://www.baseball-reference.com/leagues/majors/{season}.shtml')

    assert response.status_code == requests.status_codes.codes['ok']

    bs = BeautifulSoup(response.content, features='html.parser')
    table = bs.select_one('#teams_standard_batting')
    table_headers = [th.text for th in table.select('thead th')]
    table_rows = table.select('tbody tr')

    stats = []
    for row in table_rows:
        if 'class' in row.attrs:
            continue

        data = [row.select('th a')[0]] + row.select('td')

        observations = { 'season': season }
        observations.update(
            dict(
                zip(
                    table_headers,
                    map(lambda a: a.text, data)
                )
            )
        )

        stats.append(observations)

    return stats

@flow(name='mlb-season-stats', persist_result=False)
def get_season_stats(seasons: List[str]) -> None:
    data = []
    for season in seasons:
        data.extend(get_stats_by_season(season))

    df = pd.DataFrame(data)
    df = df.rename(columns={ 'Tm': 'team' })
    df['team'] = df.team.map(lambda name: TeamNormalizer().get(name))

    dir = './pipelines/data/mlb/season_stats.csv'
    if os.path.exists(dir):
        df_current = pd.read_csv(dir)
        df_current['season'] = df_current['season'].astype(str)

        df_current = df_current[~df_current.season.isin(seasons)]
        if not df_current.empty:
            df = pd.concat([df, df_current])

    df.sort_values(['season', 'team']).to_csv('./pipelines/data/mlb/season_stats.csv', index=False)


if __name__ == '__main__':
    get_season_stats(sys.argv[1:])
