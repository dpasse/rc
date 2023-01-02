from typing import List

import os
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from prefect import flow, task

from normalizer import TeamNormalizer


@task(retries=3)
def get_stats_by_player(player: str) -> List[dict]:
    def get_text(rows):
        return list(map(lambda r: r.text, rows))

    starts_with = player[0]
    response = requests.get(f'https://www.baseball-reference.com/players/{starts_with}/{player}.shtml')

    assert response.status_code == requests.status_codes.codes['ok']

    bs = BeautifulSoup(response.content, features='html.parser')
    table = bs.select_one('#div_batting_standard')
    table_headers = [th.text for th in table.select('thead th')]
    table_rows = table.select('tbody tr')

    stats = []
    for row in table_rows:
        tds = row.select('td')

        team = tds[1].select('a')
        if len(team) > 0:
            team = team[0].attrs['title']
        else:
            team = 'TOT'

        data = [row.select('th')[0].text] + get_text(tds[:1]) + [team] + get_text(tds[2:])

        observations = { 'player': player }
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

@flow(name='mlb-player-stats', persist_result=False)
def get_payer_stats(players: List[str]) -> None:
    data = []
    for player in players:
        data.extend(get_stats_by_player(player))

    df = pd.DataFrame(data)
    df = df.rename(columns={ 'Year': 'season', 'Tm': 'team' })

    team_normalizer = TeamNormalizer()
    df['team'] = df.team.map(lambda name: team_normalizer.get(name))

    path = '../data/mlb/player_stats.csv'
    if os.path.exists(path):
        df_current = pd.read_csv(path)
        df_current['player'] = df_current['player'].astype(str)

        df_current = df_current[~df_current.player.isin(players)]
        if not df_current.empty:
            df = pd.concat([df, df_current])

    df.sort_values(['player', 'season']).to_csv(path, index=False)


if __name__ == '__main__':
    get_payer_stats(sys.argv[1:])
