from typing import List, Optional, Tuple, Dict, Any, cast

import sys
import time
import json
import logging
import datetime
import pandas as pd

from prefect import flow, task
from common.helpers.web import make_request
from common.helpers.parsers import EventDescriptionParser


Logger = logging.getLogger(__name__)
Logger.setLevel(level=logging.INFO)
Logger.addHandler(
    logging.FileHandler('../data/mlb/logs/pbp.log')
)

EVENT_DESCRIPTION_PARSER = EventDescriptionParser()

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

    outcome = EVENT_DESCRIPTION_PARSER.transform_into_object(event['desc'])
    if outcome:
        event['entities'] = outcome

        if 'isInfoPlay' in event and not event['entities']['type'] in ['sub-p', 'sub-f']:
            if event['entities']['type'] in ['balk', 'picked off']:
                event['type'] = 'before-pitch'
            else:
                ## wild pitch, stole
                event['type'] = 'after-pitch'
    else:
        Logger.error('    - Missing entities')

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

def tie_pitch_events_to_pitch(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pitch_events: List[Dict[str, Any]] = []
    for event in events:
        if 'type' in event:
            if event['type'] in ['after-pitch', 'before-pitch']:
                pitch_events.append(event)

        elif len(pitch_events) > 0:
            if not 'pitches' in event:
                continue

            pitches = cast(List[Dict[str, Any]], event['pitches'])
            for i, pitch in enumerate(pitches):
                ## the action is on the before bases changed pitch prior to last pitch
                is_last_pitch = i == len(pitches) - 1
                should_apply_events = 'action' in pitch['result'] or is_last_pitch
                if not should_apply_events:
                    continue

                pitch_event, pitch_events = pitch_events[0], pitch_events[1:]

                if pitch_event['type'] == 'after-pitch':
                    pitch_event['afterPitchEvent'] = {
                        'id': event['id'],
                        'pitch': pitch['order']
                    }

                    pitch['result']['afterPitchEvent'] = pitch_event['id']
                else:
                    before_pitch = pitch if is_last_pitch else pitches[i+1]

                    pitch_event['beforePitchEvent'] = {
                        'id': event['id'],
                        'pitch': before_pitch['order']
                    }

                    before_pitch['result']['beforePitchEvent'] = pitch_event['id']

                if 'action' in pitch:
                    ## clear
                    del pitch['result']['action']

                if len(pitch_events) == 0:
                    break

            if len(pitch_events) > 0:
                print()
                print('NOT ALL "after-pitch" EVENTS COULD BE ACCOUNTED FOR on "action" pitches!!')
                print()

            pitch_events.clear()

    return events

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

            last_pitch = pitches[0]
            for current_pitch in pitches[1:-1]:
                if last_pitch['result']['bases'] != current_pitch['result']['bases']:
                    last_pitch['result']['action'] = True

                last_pitch = current_pitch

        events = tie_pitch_events_to_pitch(events)

    return game

def dump_json_blob(game_id: str, json_blob: dict) -> None:
    Logger.info('    - Writing debug file')

    with open(f'../data/mlb/pbp/org_pbp_{game_id}.json', 'w', encoding='UTF8') as debug_json:
        json.dump(json_blob, debug_json)

@task(retries=1, retry_delay_seconds=15)
def get_pbp(game_id: str, debug = False) -> Optional[dict]:
    Logger.info('* Stated "%s"', game_id)

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

    game = None

    try:
        game = compress_game({
            'id': game_id,
            'periods': json_obj,
        })
    except Exception as exception:
        Logger.error('    - %s failed', game_id)
        Logger.error(exception)

        debug = True

    if debug:
        dump_json_blob(
            game_id,
            json_blob=json_obj
        )

    return game

@flow(name='mlb-pbp', persist_result=False)
def get_pbps(game_ids: List[str], timeout = 8) -> None:
    for i, game_id in enumerate(game_ids):
        try:
            game = get_pbp(game_id)
            if game:
                with open(f'../data/mlb/pbp/pbp_{game_id}.json', 'w', encoding='UTF8') as pbp_output:
                    pbp_output.write(json.dumps(game, indent=2))
        except Exception as exception:
            Logger.error('    - %s failed', game_id)
            Logger.error(exception)

        if i < (len(game_ids) - 1):
            Logger.info('    - sleeping %s seconds', timeout)
            time.sleep(timeout)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        raise Exception('Need to provide options.')

    Logger.info('Started @ %s', datetime.datetime.now())

    input_game_ids: List[str] = []
    if args[0] == '-l':
        FILE_PATH = args[1]

        Logger.info('    - %s', FILE_PATH)

        df = pd.read_csv(FILE_PATH, index_col=None)
        input_game_ids.extend(
            df.id.astype(str).unique().tolist()
        )
    else:
        input_game_ids.extend(args)

    Logger.info('    - #%s', len(input_game_ids))

    get_pbps(input_game_ids, timeout=60)

    Logger.info('Finished @ %s', datetime.datetime.now())
    Logger.info('')
