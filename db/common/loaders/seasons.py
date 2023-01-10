import os
from typing import List
import pandas as pd

from ..helpers.pandas_to_sql import build_bulk_insert_sql


def execute(root_directory: str) -> List[str]:
    df_seasons = pd.read_csv(
        os.path.join(root_directory, 'seasons.csv'),
        index_col=None
    )

    return build_bulk_insert_sql(df_seasons, 'seasons')
