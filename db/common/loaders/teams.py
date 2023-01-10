import os
from typing import List
import pandas as pd

from ..helpers.pandas_to_sql import build_bulk_insert_sql


def execute(root_directory: str) -> List[str]:
    scripts = []
    for league in ['MLB']:
        df_teams = pd.read_csv(
            os.path.join(root_directory, league.lower(), 'teams.csv'),
            index_col=None
        )

        df_teams['league_id'] = league

        scripts.extend(build_bulk_insert_sql(df_teams, 'teams'))

    return scripts
