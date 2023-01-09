import sys
import time
import json
import re
import requests

from bs4 import BeautifulSoup
from typing import List, Optional
from prefect import flow, task


def clean_text(text: str) -> str:
    text = re.sub('\u00ed', 'i', text)
    return text

def parse_json(game_id: str, pbp: dict) -> dict:
    pitcher_tracker = {}

    observations = []
    for record in pbp:
        period = record['period']
        atBat = record['atBatTeam']['abbrev']
        period.update({ 'atBat': atBat })

        pitcher = re.search(r'(.+?) pitching', record['dsc'] if 'dsc' in record else '')
        if pitcher is not None:
            pitcher_tracker[atBat] = clean_text(pitcher.group(1))

        observation = {
            'period': period,
            'batters': []
        }

        for play in record['plays']:
            if 'isPitcherChange' in play and play['isPitcherChange']:
                desc =  play['dsc'] if 'dsc' in play else 'NO-IDEA pitching'
                match = re.search(r'(.+?) pitching', clean_text(desc))
                if match:
                    pitcher_tracker[atBat] = match.group(1)

            if 'pitches' in play:
                observation['batters'].append({
                    'pitcher': pitcher_tracker[atBat],
                    'dsc': clean_text(play['dsc']),
                    'pitches': [
                        {
                            'desc': pitch['dsc'],
                            'coords': pitch['ptchCoords'] if 'ptchCoords' in pitch else {'x': -1, 'y': -1},
                            'pitch': pitch['ptchDsc'] if 'ptchDsc' in pitch else '',
                            'call': pitch['rslt'],
                            'vel': pitch['vlcty'] if 'vlcty' in pitch else '',
                            'bases': [ int(i) for i in pitch['evnts']['onBase'] ] if 'evnts' in pitch and 'onBase' in pitch['evnts'] else [0, 0, 0]
                        }
                        for pitch in play['pitches']
                    ],
                })

        observations.append(observation)

    return {
        'game': game_id,
        'half-innings': observations,
    }


@task(retries=1, retry_delay_seconds=15)
def get_pbp(game_id: str) -> Optional[dict]:
    response = requests.get(f'https://www.espn.com/mlb/playbyplay/_/gameId/{game_id}')

    assert response.status_code == requests.status_codes.codes['ok']
    json_blobs = [
        script
        for script in BeautifulSoup(response.content, features='html.parser').select('script')
        if script.text.startswith("window['__espnfitt__']=")
    ]

    if len(json_blobs) == 0:
        return None

    json_blob = json_blobs[0].text
    obj = json.loads(json_blob[len('window[\'__espnfitt__\']='):-1])
    return parse_json(game_id, obj['page']['content']['gamepackage']['pbp'])


@flow(name='mlb-pbp', persist_result=False)
def get_pbps(game_ids: List[str]) -> None:
    for game_id in game_ids:
        observation = get_pbp(game_id)
        if observation:
            with open(f'../data/mlb/pbp/pbp_{game_id}.json', 'w') as pbp_output:
                pbp_output.write(json.dumps(observation, indent=2))
        else:
            print(f'Error - "{game_id}" failed')

        time.sleep(8)


if __name__ == '__main__':
    get_pbps(sys.argv[1:])
