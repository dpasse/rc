from typing import List, Optional

import os
import sys
import time
import json
import logging
import datetime
import pandas as pd

from prefect import flow, task
from common.helpers.web import make_request


Logger = logging.getLogger(__name__)
Logger.setLevel(level=logging.INFO)
Logger.addHandler(
    logging.FileHandler('../data/mlb/logs/pbp.log')
)


@task(retries=3, retry_delay_seconds=15)
def get_pbp(game_id: str) -> Optional[dict]:
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
    return json.loads(json_string)['page']['content']['gamepackage']['pbp']

@flow(name='mlb-pbp', persist_result=False)
def get_pbps(game_ids: List[str], timeout = 8) -> None:
    for i, game_id in enumerate(game_ids):
        if os.path.exists(f'../data/mlb/pbp/1/pbp_{game_id}.json'):
            Logger.info('    - skipping %s', game_id)
            continue

        try:
            json_obj = get_pbp(game_id)
            if json_obj:
                with open(f'../data/mlb/pbp/1/pbp_{game_id}.json', 'w', encoding='UTF8') as pbp_output:
                    pbp_output.write(json.dumps({ 'id': game_id, 'periods': json_obj }, indent=2))
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

    Logger.info('Started Download @ %s', datetime.datetime.now())

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

    get_pbps(input_game_ids, timeout=30)

    Logger.info('Finished Download @ %s', datetime.datetime.now())
    Logger.info('')
