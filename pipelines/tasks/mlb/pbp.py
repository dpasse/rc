import sys
import time
import json

from typing import List, Optional
from prefect import flow, task

from common.helpers.web import make_request


def compress_game(game: dict) -> dict:
    if len(game['periods']):
        first_child = game['periods'][0]
        game.update({
          'away': first_child['awayTeamShortName'].lower(),
          'home': first_child['homeTeamShortName'].lower(),
        })

        for data in game['periods']:
            if 'atBatTeam' in data:
                data['atBat'] = data['atBatTeam']['abbrev'].lower()
                del data['atBatTeam']

            if 'period' in data:
                period = data['period']
                data['id'] = f"{period['type']}-{period['number']}".lower()
                del data['period']

            if 'awayTeamShortName' in data:
                del data['awayTeamShortName']

            if 'homeTeamShortName' in data:
                del data['homeTeamShortName']

            if 'dsc' in data:
                data['plays'] = [{ 'desc': data['dsc'] }] + data['plays']
                del data['dsc']

            if 'plays' in data:
                data['events'] = data['plays']
                del data['plays']

            data['score'] = {
                'runs': int(data['runs']),
                'hits': int(data['hits']),
                'errors': int(data['errors'])
            }

            del data['hits']
            del data['runs']
            del data['errors']

            if 'events' in data:
                previous_bases = None
                for event in data['events']:
                    if 'defaultOpen' in event:
                        del event['defaultOpen']

                    if 'awayScore' in event and 'homeScore' in event:
                        event['score'] = {
                            'away': event['awayScore'],
                            'home': event['homeScore']
                        }

                        del event['awayScore']
                        del event['homeScore']

                    if 'isAway' in event:
                        del event['isAway']

                    if 'id' in event:
                        del event['id']

                    if 'dsc' in event:
                        event['desc'] = event['dsc']
                        del event['dsc']

                    if 'pitches' in event:
                        for pitch in event['pitches']:

                            if 'id' in pitch:
                                del pitch['id']

                            if 'ptchCoords' in pitch:
                                pitch['coords'] = pitch['ptchCoords']
                                del pitch['ptchCoords']

                            if 'vlcty' in pitch:
                                pitch['velocity'] = pitch['vlcty']
                                del pitch['vlcty']

                            if 'rslt' in pitch:
                                pitch['result'] = {
                                    'type': pitch['rslt'].lower(),
                                }

                                if 'dsc' in pitch:
                                    pitch['result']['outcome'] = pitch['dsc'].lower()
                                    del pitch['dsc']

                                if 'hitCoords' in pitch:
                                    pitch['result']['hitCoords'] = pitch['hitCoords']
                                    del pitch['hitCoords']

                                del pitch['rslt']

                            if 'ptchDsc' in pitch:
                                pitch['type'] = pitch['ptchDsc'].lower()
                                del pitch['ptchDsc']

                            if 'evnts' in pitch and 'onBase' in pitch['evnts']:
                                pitch['bases'] = [int(x) for x in pitch['evnts']['onBase']]
                                del pitch['evnts']['onBase']

                                previous_bases = pitch['bases'].copy()

                                if len(pitch['evnts'].keys()) == 0:
                                    del pitch['evnts']
                            elif previous_bases:
                                pitch['bases'] = previous_bases.copy()

    return game

@task(retries=1, retry_delay_seconds=15)
def get_pbp(game_id: str) -> Optional[dict]:
    key = "window['__espnfitt__']="

    scripts = make_request(
        f'https://www.espn.com/mlb/playbyplay/_/gameId/{game_id}'
    ).select('script')

    json_blobs = [
        script
        for script in scripts
        if script.text.startswith(key)
    ]

    if len(json_blobs) == 0:
        return None

    json_string = json_blobs[0].text[len(key):-1]
    json_obj = json.loads(json_string)['page']['content']['gamepackage']['pbp']

    observation = {
      'id': game_id,
      'periods': json_obj,
    }

    return compress_game(observation)

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
