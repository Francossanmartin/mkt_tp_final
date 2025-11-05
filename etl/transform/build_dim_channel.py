import pandas as pd
from . import make_sk_map

def build_dim_channel(channel: pd.DataFrame) -> pd.DataFrame:
    dim = channel.rename(columns={"channel_id":"channel_bk"}).copy()
    sk = make_sk_map(dim, "channel_bk", "channel_sk")
    dim = dim.merge(sk, on="channel_bk", how="left")
    return dim[["channel_sk","channel_bk","code","name"]].drop_duplicates()


