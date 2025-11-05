import pandas as pd
from . import to_datetime

def _from_series(s: pd.Series) -> pd.DataFrame:
    s = pd.to_datetime(s.dropna().unique())
    df = pd.DataFrame({"date": s})
    df["date_key"] = df["date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["dow"] = df["date"].dt.dayofweek + 1
    df["is_weekend"] = df["dow"].isin([6,7]).astype(int)
    return df

def build_dim_date(sales_order, shipment, payment) -> pd.DataFrame:
    so = to_datetime(sales_order.copy(), ["order_date"])
    sh = to_datetime(shipment.copy(), ["shipped_at","delivered_at"])
    pay = to_datetime(payment.copy(), ["paid_at"])
    dim = pd.concat([
        _from_series(so["order_date"]),
        _from_series(sh["shipped_at"]),
        _from_series(sh["delivered_at"]),
        _from_series(pay["paid_at"]),
    ], ignore_index=True).drop_duplicates(subset=["date_key"]).sort_values("date_key")
    dim = dim.reset_index(drop=True); dim["date_sk"] = dim.index + 1
    return dim[["date_sk","date_key","date","year","quarter","month","month_name","day","dow","is_weekend"]]
