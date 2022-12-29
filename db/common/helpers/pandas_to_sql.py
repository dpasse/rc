import numpy as np
import pandas as pd
from typing import List


def chunkify(df: pd.DataFrame, chunk_size: int):
    ## simple helper found -> https://stackoverflow.com/questions/44729727/pandas-slice-large-dataframe-into-chunks
    start = 0
    length = df.shape[0]

    if length <= chunk_size:
        yield df[:]
        return

    while start + chunk_size <= length:
        yield df[start:chunk_size + start]
        start = start + chunk_size

    if start < length:
        yield df[start:]


def build_bulk_insert_sql(df: pd.DataFrame, table_name: str, chunk_size: int=1000) -> List[str]:
    dtypes = list(df.dtypes.to_dict().items())
    column_names = ', '.join(df.columns)
    df = df.fillna(np.nan).replace([np.nan], [None])

    insert_statements = []
    for chunk in chunkify(df, chunk_size):
        sql = f"""INSERT INTO {table_name} ({column_names}) VALUES"""

        for _, row in chunk.iterrows():
            insertable = []
            for col, dtype in dtypes:
                value = row[col]
                if dtype.name == 'object' and not value is None:
                    insertable.append('"' + str(row[col]).strip() + '"')
                elif value is None:
                    insertable.append('NULL')
                else:
                    insertable.append(str(row[col]))

            insertable_sql = ', '.join(insertable)
            sql += f'\n({insertable_sql}),'

        insert_statements.append(sql[:-1])

    return insert_statements