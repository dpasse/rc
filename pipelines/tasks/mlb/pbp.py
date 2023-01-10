import sys
import time
import json

from typing import List, Optional, Tuple, Dict, Any, cast
from prefect import flow, task
from common.helpers.web import make_request


def transform_at_bat(period: Dict[str, Any]) -> Dict[str, Any]:
    if 'atBatTeam' in period:
        period['atBat'] = period['atBatTeam']['abbrev'].lower()

        del period['atBatTeam']

    return period

def transform_period(period: Dict[str, Any]) -> Dict[str, Any]:
    if 'period' in period:
        period['id'] = f"{period['period']['type']}-{period['period']['number']}".lower()

        del period['period']

    return period

def transform_plays(period: Dict[str, Any]) -> Dict[str, Any]:
    if 'plays' in period:
        period['events'] = period['plays']

        del period['plays']

    if 'dsc' in period:
        period['events'] = [{ 'desc': period['dsc'] }] + period['events']

        del period['dsc']

    return period

def transform_score(period: Dict[str, Any]) -> Dict[str, Any]:
    period['score'] = {
        'runs': int(period['runs']),
        'hits': int(period['hits']),
        'errors': int(period['errors'])
    }

    return period

def clean_period(period: Dict[str, Any]) -> Dict[str, Any]:
    del period['hits']
    del period['runs']
    del period['errors']
    del period['awayTeamShortName']
    del period['homeTeamShortName']

    return period

def transform_event_score(event: Dict[str, Any]) -> Dict[str, Any]:
    if 'awayScore' in event and 'homeScore' in event:
        event['score'] = {
            'away': event['awayScore'],
            'home': event['homeScore']
        }

        del event['awayScore']
        del event['homeScore']

    return event

def transform_event_desc(event: Dict[str, Any]) -> Dict[str, Any]:
    if 'dsc' in event:
        event['desc'] = event['dsc']
        del event['dsc']

    return event

def clean_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if 'defaultOpen' in event:
        del event['defaultOpen']

    if 'isAway' in event:
        del event['isAway']

    if 'id' in event:
        del event['id']

    return event

def transform_pitch_renames(pitch: Dict[str, Any]) -> Dict[str, Any]:
    if 'ptchCoords' in pitch:
        pitch['coords'] = pitch['ptchCoords']
        del pitch['ptchCoords']

    if 'vlcty' in pitch:
        pitch['velocity'] = pitch['vlcty']
        del pitch['vlcty']

    if 'ptchDsc' in pitch:
        pitch['type'] = pitch['ptchDsc'].lower()
        del pitch['ptchDsc']

    return pitch

def transform_pitch_result(pitch: Dict[str, Any]) -> Dict[str, Any]:
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

    return pitch

def transform_pitch_bases_event(pitch: Dict[str, Any], previous_bases: List[int]) -> Tuple[Dict[str, Any], List[int]]:
    if 'evnts' in pitch and 'onBase' in pitch['evnts']:
        bases = [int(x) for x in pitch['evnts']['onBase']]

        pitch['bases'] = bases
        previous_bases = bases.copy()

        del pitch['evnts']['onBase']

        if len(pitch['evnts'].keys()) == 0:
            del pitch['evnts']
    else:
        pitch['bases'] = previous_bases.copy()

    return pitch, previous_bases

def transform_clean_pitch(pitch: Dict[str, Any]) -> Dict[str, Any]:
    if 'id' in pitch:
        del pitch['id']

    return pitch

def compress_game(game: Dict[str, Any]) -> Dict[str, Any]:
    if len(game['periods']) == 0:
        return game

    game.update({
        'away': game['periods'][0]['awayTeamShortName'].lower(),
        'home': game['periods'][0]['homeTeamShortName'].lower(),
    })

    for period in cast(List[Dict[str, Any]], game['periods']):
        for transformer in (
            transform_at_bat,
            transform_period,
            transform_plays,
            transform_score,
            clean_period,
        ):
            period = transformer(period)

        if not 'events' in period:
            continue

        previous_bases = [0, 0, 0]
        for event in cast(List[Dict[str, Any]], period['events']):
            for event_transformer in (
                transform_event_score,
                transform_event_desc,
                clean_event,
            ):
                event = event_transformer(event)

            if not 'pitches' in event:
                continue

            for pitch in cast(List[Dict[str, Any]], event['pitches']):
                for pitch_transformer in (
                    transform_pitch_renames,
                    transform_pitch_result,
                    transform_clean_pitch,
                ):
                    pitch = pitch_transformer(pitch)

                pitch, previous_bases = transform_pitch_bases_event(pitch, previous_bases)

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
            with open(f'../data/mlb/pbp/pbp_{game_id}.json', 'w', encoding='UTF8') as pbp_output:
                pbp_output.write(json.dumps(observation, indent=2))
        else:
            print(f'Error - "{game_id}" failed')

        time.sleep(8)


if __name__ == '__main__':
    get_pbps(sys.argv[1:])
