import pandas as pd
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

    df['OBP+SLG'] = df['OBP'] + df['SLG']
    return df

def team(df: pd.DataFrame, team_normalizer=TeamNormalizer()) -> pd.DataFrame:
    df['team_name'] = df['team'].copy()
    df['team'] = df['team'].map(lambda name: team_normalizer.get(name))

    return df

__all__ = [
    single,
    hbp_plus_bb,
    obp_plus_slg,
    team,
]

def run(df: pd.DataFrame, transformers: list = __all__) -> pd.DataFrame:
    for transformer in transformers:
        df = transformer(df)

    return df
