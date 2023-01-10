from typing import List, cast

import os
import sys
import time
import pandas as pd
from prefect import flow, task

from common.helpers.transformers import run, PITCHERS
from common.helpers.web import make_request


@task(retries=3)
def get_pitcher_stats(player: str) -> List[dict]:
    def get_text(rows):
        return list(map(lambda r: r.text, rows))

    table = make_request(
        f'https://www.baseball-reference.com/players/{player[0]}/{player}.shtml'
    ).select_one('#div_pitching_standard')

    if table is None:
        raise KeyError('#div_pitching_standard was not found in html')

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
def get_aggregates(players: List[str]) -> None:
    data: List[dict] = []
    for player in players:
        data.extend(cast(List[dict], get_pitcher_stats(player)))

        time.sleep(8)

    df = pd.DataFrame(data)
    df = df.rename(columns={
        'Year': 'season',
        'Tm': 'team',
        'SO': 'K'
    })
    df = df.drop(columns=['Awards'])
    df = run(df, PITCHERS)

    path = '../data/mlb/pitchers/pitcher_aggregates.csv'
    if os.path.exists(path):
        df_current = pd.read_csv(path)
        df_current['player'] = df_current['player'].astype(str)

        df_current = df_current[~df_current.player.isin(players)]
        if not df_current.empty:
            df = pd.concat([df, df_current])

    df.sort_values(['player', 'season']).to_csv(path, index=False)


if __name__ == '__main__':
    get_aggregates(sys.argv[1:])
