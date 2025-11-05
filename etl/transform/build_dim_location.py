import pandas as pd
from . import make_sk_map

def build_dim_location(address: pd.DataFrame, province: pd.DataFrame) -> pd.DataFrame:
    a = address.rename(columns={"address_id":"address_bk","province_id":"province_bk"}).copy()
    p = province.rename(columns={"province_id":"province_bk","name":"province_name","code":"province_code"})
    d = a.merge(p, on="province_bk", how="left")
    sk = make_sk_map(d, "address_bk", "location_sk")
    d = d.merge(sk, on="address_bk", how="left")
    keep = ["location_sk","address_bk","city","province_name","province_code","postal_code","country_code"]
    return d[keep].drop_duplicates()
