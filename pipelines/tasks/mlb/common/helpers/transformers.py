from typing import List, Tuple
import pandas as pd
import numpy as np
from .normalizers import TeamNormalizer
from functools import partial, wraps


def _pseudo_set_types(f, types: List[Tuple[List[str], type]]):
    @wraps(f)
    def wrapper(df, *args, **kwargs):
        for columns, type in types:
            for column in columns:
                df[column] = df[column].astype(type)

        return f(df, *args, **kwargs)

    return wrapper

@(partial(_pseudo_set_types, types=[(['H', '2B', '3B', 'HR'], int)]))
def single(df: pd.DataFrame) -> pd.DataFrame:
    df['1B'] = df['H'] - (df['2B'] + df['3B'] + df['HR'])
    return df

@(partial(_pseudo_set_types, types=[(['HBP', 'BB'], int)]))
def hbp_plus_bb(df: pd.DataFrame) -> pd.DataFrame:
    df['HBP+BB'] = df['HBP'] + df['BB']
    return df

@(partial(_pseudo_set_types, types=[(['OBP', 'SLG'], float)]))
def obp_plus_slg(df: pd.DataFrame) -> pd.DataFrame:
    df['OBP+SLG'] = (df['OBP'] + df['SLG']).round(5)
    return df

@(partial(_pseudo_set_types, types=[(['HR', 'K', 'HBP+BB'], int), (['IP'], float)]))
def dice(df: pd.DataFrame) ->  pd.DataFrame:
    # Defense-Independent Component ERA (PREDICT FUTURE ERA)
    df['DICE'] = (3.0 + ((13 * df['HR'] + 3 * df['HBP+BB'] - 2 * df['K']) / df['IP'])).round(5)
    return df

@(partial(_pseudo_set_types, types=[(['RA', 'RS'], int)]))
def pythagorean(df: pd.DataFrame, exp=2.0) -> pd.DataFrame:
    key = str(exp).replace('.', '_')
    rate = np.power((df['RS'] / df['RA']), exp)
    df[f'PYTH_{key}'] = (rate / (rate + 1)).round(3)
    return df

def team(df: pd.DataFrame, team_normalizer=TeamNormalizer()) -> pd.DataFrame:
    df['team_name'] = df['team'].astype(str).copy()
    df['team'] = df['team'].map(lambda name: team_normalizer.get(name)).astype(int)
    return df

BATTERS = [
    single,
    hbp_plus_bb,
    obp_plus_slg,
    team,
]

PITCHERS = [
    hbp_plus_bb,
    dice,
    team,
]

def run(df: pd.DataFrame, transformers: list = BATTERS) -> pd.DataFrame:
    for transformer in transformers:
        df = transformer(df)

    return df
