from typing import List, Optional, Tuple, Dict, Any, cast

import os
import json
import logging
import datetime

from prefect import flow, task
from common.helpers.parsers import parse_game
from common.helpers.extractors import get_game_issues


PBP_DOWNLOAD_DIRECTORY = '../data/mlb/pbp/1/'
PBP_OUTPUT_DIRECTORY = '../data/mlb/pbp/2/'

Logger = logging.getLogger(__name__)
Logger.setLevel(level=logging.INFO)
Logger.addHandler(
    logging.FileHandler('../data/mlb/logs/pbp.log')
)

# pylint: disable=W0703

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

def transform_events(period: Dict[str, Any]) -> Dict[str, Any]:
    if 'plays' in period:
        period['events'] = period['plays']

        del period['plays']

    if 'dsc' in period:
        period['events'] = [{ 'desc': period['dsc'], 'isInfoPlay': True }] + period['events']

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

    if 'count' in pitch:
        pitch['order'] = pitch['count']
        del pitch['count']

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
    else:
        pitch['result'] = {}

    return pitch

def transform_pitch_bases_event(pitch: Dict[str, Any], previous_bases: List[int]) -> Tuple[Dict[str, Any], List[int]]:
    if 'evnts' in pitch and 'onBase' in pitch['evnts']:
        bases = [int(x) for x in pitch['evnts']['onBase']]

        pitch['result']['bases'] = bases
        previous_bases = bases.copy()

        del pitch['evnts']['onBase']

        if len(pitch['evnts'].keys()) == 0:
            del pitch['evnts']
    else:
        pitch['result']['bases'] = previous_bases.copy()

    return pitch, previous_bases

def transform_pitch_set_count(pitch: Dict[str, Any], count: dict) -> Tuple[Dict[str, Any], dict]:
    pitch['count'] = count.copy()
    if pitch['result']['type'] == 'strike' or (count['strikes'] < 2 and pitch['result']['type'] == 'foul'):
        count['strikes'] += 1

    count['balls'] += int(pitch['result']['type'] == 'ball')

    return pitch, count

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

    i = 1
    for period in cast(List[Dict[str, Any]], game['periods']):
        for transformer in (
            transform_at_bat,
            transform_period,
            transform_events,
            transform_score,
            clean_period,
        ):
            period = transformer(period)

        if not 'events' in period:
            continue

        previous_bases = [0, 0, 0]
        events = cast(List[Dict[str, Any]], period['events'])
        for event in events:
            for event_transformer in (
                transform_event_score,
                transform_event_desc,
                clean_event,
            ):
                event = event_transformer(event)

            event['id'] = i
            i += 1

            if not 'pitches' in event:
                continue

            count = {
                'balls': 0,
                'strikes': 0,
            }

            pitches = cast(List[Dict[str, Any]], event['pitches'])
            if len(pitches) == 0:
                continue

            for pitch in pitches:
                for pitch_transformer in (
                    transform_pitch_renames,
                    transform_pitch_result,
                    transform_clean_pitch,
                ):
                    pitch = pitch_transformer(pitch)

                pitch, previous_bases = transform_pitch_bases_event(pitch, previous_bases)
                pitch, count = transform_pitch_set_count(pitch, count)

    return game

@task(retries=1, retry_delay_seconds=15)
def get_pbp(game: dict) -> Optional[dict]:
    Logger.info('* Stated "%s"', game['id'])

    try:
        game = parse_game(
            compress_game(game)
        )
    except Exception as exception:
        Logger.error('    - %s failed', game['id'])
        Logger.error(exception)

    return game

@task(retries=1, retry_delay_seconds=15)
def get_games() -> List[dict]:
    games: List[dict] = []
    for file in os.listdir(PBP_DOWNLOAD_DIRECTORY):
        with open(os.path.join(PBP_DOWNLOAD_DIRECTORY, file), 'r', encoding='UTF8') as pbp:
            games.append(
                json.loads(pbp.read())
            )

    return games

@flow(name='mlb-pbp', persist_result=False)
def get_pbps() -> None:
    games = get_games.submit().result()

    for game in games:
        try:
            game_id = game['id']
            parsed_game = get_pbp.submit(game).result()
            if parsed_game:
                with open(os.path.join(PBP_OUTPUT_DIRECTORY, f'pbp_{game_id}.json'), 'w', encoding='UTF8') as pbp_output:
                    pbp_output.write(json.dumps(parsed_game, indent=2))

                issues = get_game_issues(parsed_game)
                if len(issues['periods']) > 0:
                    Logger.error('ISSUES FOUND:')
                    Logger.error(issues)
        except Exception as exception:
            Logger.error('    - %s failed', game_id)
            Logger.error(exception)


if __name__ == '__main__':
    Logger.info('Started Parsing @ %s', datetime.datetime.now())

    get_pbps()

    Logger.info('Finished @ %s', datetime.datetime.now())
    Logger.info('')
