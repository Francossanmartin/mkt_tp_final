# etl/transform/build_fact_shipment.py
import pandas as pd
# si querés, podés usar también: from . import to_datetime
# pero no es necesario; acá uso pd.to_datetime directamente.

def build_fact_shipment(shipment: pd.DataFrame, dim_date: pd.DataFrame) -> pd.DataFrame:
    # Normalizo columnas base
    s = shipment.rename(columns={"order_id": "order_bk"}).copy()

    # Aseguro tipos datetime (no rompe si ya vienen en datetime)
    for col in ["shipped_at", "delivered_at"]:
        if col in s.columns:
            s[col] = pd.to_datetime(s[col], errors="coerce")
        else:
            # si falta alguna columna de fecha, la creo vacía para no romper
            s[col] = pd.NaT

    # Claves de fecha (YYYYMMDD) para matchear contra dim_date.date_key
    s["shipped_key"]   = s["shipped_at"].dt.strftime("%Y%m%d").astype("Int64")
    s["delivered_key"] = s["delivered_at"].dt.strftime("%Y%m%d").astype("Int64")

    # Mapas desde dim_date: date_key -> date_sk
    map_shipped = (
        dim_date.rename(columns={"date_key": "shipped_key", "date_sk": "shipped_date_sk"})
                [["shipped_key", "shipped_date_sk"]]
    )
    map_deliv = (
        dim_date.rename(columns={"date_key": "delivered_key", "date_sk": "delivered_date_sk"})
                [["delivered_key", "delivered_date_sk"]]
    )

    # Joins para traer los SK
    s = s.merge(map_shipped, on="shipped_key", how="left")
    s = s.merge(map_deliv, on="delivered_key", how="left")

    # Flag de entrega
    s["is_delivered"] = (~s["delivered_at"].isna()).astype(int)

    # Selección columnas finales
    cols = ["order_bk", "carrier", "tracking_number", "shipped_date_sk", "delivered_date_sk", "is_delivered"]
    # por si falta alguna en el raw, las creo vacías
    for c in ["carrier", "tracking_number"]:
        if c not in s.columns:
            s[c] = pd.NA

    return s[cols]
