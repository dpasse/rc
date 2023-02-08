import os
from typing import List
import pandas as pd

from ...helpers.pandas import build_bulk_insert_sql


def execute(root_directory: str) -> List[str]:
    df_leagues = pd.read_csv(
        os.path.join(root_directory, 'leagues.csv'),
        index_col=None
    )

    return build_bulk_insert_sql(df_leagues, 'leagues')
