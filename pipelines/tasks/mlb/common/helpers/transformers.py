import pandas as pd
import numpy as np
from .normalizers import TeamNormalizer


def single(df: pd.DataFrame) -> pd.DataFrame:
    for column in ['H', '2B', '3B', 'HR']:
        df[column] = df[column].astype(int)

    df['1B'] = df['H'] - (df['2B'] + df['3B'] + df['HR'])

    return df

def hbp_plus_bb(df: pd.DataFrame) -> pd.DataFrame:
    for column in ['HBP', 'BB']:
        df[column] = df[column].astype(int)

    df['HBP+BB'] = df['HBP'] + df['BB']

    return df

def obp_plus_slg(df: pd.DataFrame) -> pd.DataFrame:
    for column in ['OBP', 'SLG']:
        df[column] = df[column].astype(float)

    df['OBP+SLG'] = (df['OBP'] + df['SLG']).round(5)
    return df

def dice(df: pd.DataFrame) ->  pd.DataFrame:
    # Defense-Independent Component ERA (PREDICT FUTURE ERA)

    for column in ['HR', 'K', 'HBP+BB']:
        df[column] = df[column].astype(int)

    for column in ['IP']:
        df[column] = df[column].astype(float)

    df['DICE'] = (3.0 + ((13 * df['HR'] + 3 * df['HBP+BB'] - 2 * df['K']) / df['IP'])).round(5)
    return df

def pythagorean(df: pd.DataFrame, exp=2.0) -> pd.DataFrame:
    for column in ['RA', 'RS']:
        df[column] = df[column].astype(int)

    key = str(exp).replace('.', '_')
    rate = np.power((df['RS'] / df['RA']), exp)
    df[f'PYTH_{key}'] = (rate / (rate + 1)).round(3)
    return df

def team(df: pd.DataFrame, team_normalizer=TeamNormalizer()) -> pd.DataFrame:
    df['team_name'] = df['team'].copy()
    df['team'] = df['team'].map(lambda name: team_normalizer.get(name))

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
