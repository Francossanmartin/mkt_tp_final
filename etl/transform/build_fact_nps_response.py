import pandas as pd

def build_fact_nps_response(nps, dim_customer, dim_channel, dim_date):
    # Renombrar BKs
    n = nps.rename(columns={
        "nps_id": "nps_bk",
        "customer_id": "customer_bk",
        "channel_id": "channel_bk"
    }).copy()

    # ---- Fecha -> responded_key (YYYYMMDD como entero nullable) ----
    # Si no existe responded_at, quedará NaT y luego NaN en la key
    n["responded_at"] = pd.to_datetime(n.get("responded_at"), errors="coerce")
    n["responded_key"] = (
        n["responded_at"]
        .dt.strftime("%Y%m%d")
        .pipe(pd.to_numeric, errors="coerce")
        .astype("Int64")  # permite nulos
    )

    # ---- SKs de dimensiones ----
    n = (
        n.merge(dim_customer[["customer_bk", "customer_sk"]], on="customer_bk", how="left")
         .merge(dim_channel[["channel_bk", "channel_sk"]], on="channel_bk", how="left")
    )

    # ---- Traer date_sk desde dim_date por date_key ----
    n = n.merge(
        dim_date[["date_sk", "date_key"]].rename(columns={"date_key": "responded_key"}),
        on="responded_key",
        how="left"
    )

    # ---- Métricas / columnas numéricas ----
    n["score"] = pd.to_numeric(n.get("score", 0), errors="coerce").fillna(0)

    # Asegurar columna comment aunque no exista en RAW
    if "comment" not in n.columns:
        n["comment"] = pd.NA

    # ---- Selección final ----
    n = n.rename(columns={"date_sk": "responded_date_sk"})
    keep = ["nps_bk", "customer_sk", "channel_sk", "responded_date_sk", "score", "comment"]
    for c in keep:
        if c not in n.columns:
            n[c] = pd.NA

    return n[keep]
