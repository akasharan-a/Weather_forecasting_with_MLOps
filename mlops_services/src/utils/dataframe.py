import polars as pl

def column_count(df):
    stat = df.to_dict(as_series=False)
    stat = {k:stat[0] for k in stat}
    