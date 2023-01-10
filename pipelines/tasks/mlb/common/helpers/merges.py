import pandas as pd


def merge(df, df_current) -> pd.DataFrame:
    if not df_current.empty:
        df = pd.concat([df, df_current])

    return df
