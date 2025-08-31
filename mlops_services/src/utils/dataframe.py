import os
from pathlib import Path
import polars as pl

pl_df = pl.DataFrame()

def load_parquet(folder, filename):
    try:
        df = pl.read_parquet(Path(folder) / f"{filename}.parquet")
    except Exception as e:
        raise e
    return df    
def column_count(df):
    stat = df.to_dict(as_series=False)
    stat = {k:stat[0] for k in stat}
    