from typing import List, cast

import os
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from prefect import flow, task

from common.helpers.transformers import run, PITCHERS


@task(retries=3)
def get_season_stats(season: str) -> List[dict]:
    response = requests.get(f'https://www.baseball-reference.com/leagues/majors/{season}-standard-pitching.shtml')

    assert response.status_code == requests.status_codes.codes['ok']

    bs = BeautifulSoup(response.content, features='html.parser')
    table = bs.select_one('#teams_standard_pitching')
    if table is None:
        raise KeyError('#teams_standard_pitching was not found in html')

    table_headers = [th.text for th in table.select('thead th')]
    table_rows = table.select('tbody tr')

    stats: List[dict] = []
    for row in table_rows:
        if 'class' in row.attrs:
            continue

        observations: dict = { 'season': season }
        observations.update(
            dict(
                zip(
                    table_headers,
                    map(lambda a: a.text, [row.select('th a')[0]] + row.select('td'))
                )
            )
        )

        stats.append(observations)

    return stats

@flow(name='mlb-season-pitching-aggregates', persist_result=False)
def get_season_aggregates(seasons: List[str]) -> None:
    data: List[dict] = []
    for season in seasons:
        data.extend(cast(List[dict], get_season_stats(season)))

    df = pd.DataFrame(data)
    df = df.rename(columns={
        'Tm': 'team',
        'SO': 'K'
    })
    df = run(df, PITCHERS)

    path = '../data/mlb/pitchers/season_aggregates.csv'
    if os.path.exists(path):
        df_current = pd.read_csv(path)
        df_current['season'] = df_current['season'].astype(str)

        df_current = df_current[~df_current.season.isin(seasons)]
        if not df_current.empty:
            df = pd.concat([df, df_current])

    df.sort_values(['season', 'team']).to_csv(path, index=False)


if __name__ == '__main__':
    get_season_aggregates(sys.argv[1:])
