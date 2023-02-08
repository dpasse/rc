from typing import List, cast

import os
import sys
import time
import pandas as pd
from prefect import flow, task

# pylint: disable=C0413

from setup_module import append_path

append_path()

from mushbeard.helpers.transformers import run, PITCHERS, BATTERS
from mushbeard.helpers.web import make_request
from mushbeard.helpers.pandas import merge


@task(retries=3)
def get_stats(aggregate_type: str, player: str) -> List[dict]:
    def get_text(rows):
        return list(map(lambda r: r.text, rows))

    table = make_request(
        f'https://www.baseball-reference.com/players/{player[0]}/{player}.shtml'
    ).select_one(f'#div_{aggregate_type}_standard')

    if table is None:
        raise KeyError(f'#div_{aggregate_type}_standard was not found in html')

    table_headers = [th.text for th in table.select('thead th')]
    table_rows = table.select('tbody tr')

    stats: List[dict] = []
    for row in table_rows:
        if 'spacer' in row.attrs['class']:
            continue

        tds = row.select('td')

        team_obj = tds[1].select('a')
        team = team_obj[0].attrs['title'] if len(team_obj) > 0 else 'TOT'

        data = [row.select('th')[0].text] \
            + get_text(tds[:1]) \
            + [team] \
            + get_text(tds[2:])

        observations: dict = { 'player': player }
        observations.update(
            dict(
                zip(
                    table_headers,
                    data
                )
            )
        )

        stats.append(observations)

    return stats

@flow(name='mlb-pitcher-aggregates', persist_result=False)
def get_aggregates(aggregate_type: str, players: List[str]) -> None:
    data: List[dict] = []
    for player in players:
        data.extend(cast(List[dict], get_stats(aggregate_type, player)))

        time.sleep(8)

    df = pd.DataFrame(data)
    df = df.rename(columns={
        'Year': 'season',
        'Tm': 'team',
        'SO': 'K'
    })
    df = df.drop(columns=['Awards'])
    df = run(df, PITCHERS if aggregate_type == 'pitching' else BATTERS)

    path = f'../data/mlb/{aggregate_type}/player_aggregates.csv'
    if os.path.exists(path):
        df_current = pd.read_csv(path)
        df_current['player'] = df_current['player'].astype(str)

        df = merge(df, df_current[~df_current.player.isin(players)])

    df.sort_values(['player', 'season']).to_csv(path, index=False)


if __name__ == '__main__':
    get_aggregates(sys.argv[1], sys.argv[2:])
