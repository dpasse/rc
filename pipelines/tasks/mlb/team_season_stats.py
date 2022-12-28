from typing import List

import requests
import pandas as pd
from bs4 import BeautifulSoup
from prefect import flow, task


@task(retries=3)
def get_stats_by_season(season: str) -> List[dict]:
    stats = []

    bs = BeautifulSoup(
        requests.get(f'https://www.baseball-reference.com/leagues/majors/{season}.shtml').content,
        features='html.parser'
    )

    table_headers = [th.text for th in bs.select('.stats_table thead th')]
    table_rows = bs.select('.stats_table tbody tr')

    for row in table_rows:
        if 'class' in row.attrs:
            continue

        observations = { 'season': season }
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

@flow(name='mlb-season-stats', persist_result=False)
def get_season_stats(seasons: List[str]) -> None:
    data = []
    for season in seasons:
        data.extend(get_stats_by_season(season))

    pd.DataFrame(data).to_csv('./pipelines/data/mlb/season_stats.csv')


if __name__ == '__main__':
    seasons = [
        '2021',
        '2022'
    ]

    get_season_stats(seasons)
