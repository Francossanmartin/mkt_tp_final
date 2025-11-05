import pandas as pd

def build_fact_web_session(
    web_session: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_channel: pd.DataFrame,
    dim_date: pd.DataFrame
) -> pd.DataFrame:
    """
    Construye la tabla de hechos de sesiones web uniendo con dim_customer, dim_channel y dim_date.
    Salida:
      session_bk, customer_sk, channel_sk, started_date_sk, ended_date_sk, device, is_ended
    """

    # Copia segura (y formato vacío compatible si viene None)
    if web_session is None or not isinstance(web_session, pd.DataFrame):
        return pd.DataFrame(columns=[
            "session_bk","customer_sk","channel_sk","started_date_sk","ended_date_sk","device","is_ended"
        ])
    ws = web_session.copy()

    # Renombrar BKs si existen; crear si faltan (evita KeyError en merges)
    rename_map = {"session_id": "session_bk", "customer_id": "customer_bk", "channel_id": "channel_bk"}
    ws = ws.rename(columns={k: v for k, v in rename_map.items() if k in ws.columns})
    for col in ["session_bk", "customer_bk", "channel_bk"]:
        if col not in ws.columns:
            ws[col] = pd.NA

    # Asegurar datetimes
    for col in ["started_at", "ended_at"]:
        if col in ws.columns:
            ws[col] = pd.to_datetime(ws[col], errors="coerce")
        else:
            ws[col] = pd.NaT

    # Keys YYYYMMDD robustas (toleran NaT)
    def _to_key(dt_series: pd.Series) -> pd.Series:
        s = dt_series.dt.strftime("%Y%m%d")                     # strings (o NaT)
        num = pd.to_numeric(s, errors="coerce")                 # float con NaN
        return num.astype("Int64")                              # Int64 con <NA>

    ws["start_key"] = _to_key(ws["started_at"])
    ws["end_key"]   = _to_key(ws["ended_at"])

    # Normalizar dim_date para asegurar date_key Int64
    dd = dim_date.copy() if isinstance(dim_date, pd.DataFrame) else pd.DataFrame()
    if "date_key" in dd.columns:
        dd["date_key"] = pd.to_numeric(dd["date_key"], errors="coerce").astype("Int64")
    elif "date" in dd.columns:
        dd["date"] = pd.to_datetime(dd["date"], errors="coerce")
        dd["date_key"] = pd.to_numeric(dd["date"].dt.strftime("%Y%m%d"), errors="coerce").astype("Int64")
    else:
        # Sin date_key ni date no se puede mapear
        return pd.DataFrame(columns=[
            "session_bk","customer_sk","channel_sk","started_date_sk","ended_date_sk","device","is_ended"
        ])

    # Validar columnas críticas en dim_date
    if "date_sk" not in dd.columns:
        return pd.DataFrame(columns=[
            "session_bk","customer_sk","channel_sk","started_date_sk","ended_date_sk","device","is_ended"
        ])

    # Mapas de date_key → date_sk
    map_start = dd.rename(columns={"date_key": "start_key", "date_sk": "started_date_sk"})[["start_key", "started_date_sk"]].drop_duplicates()
    map_end   = dd.rename(columns={"date_key": "end_key",   "date_sk": "ended_date_sk"})  [["end_key",   "ended_date_sk"]].drop_duplicates()

    # Subsets de dims (y asegurar columnas críticas)
    dc = dim_customer.copy() if isinstance(dim_customer, pd.DataFrame) else pd.DataFrame()
    if not {"customer_bk","customer_sk"}.issubset(dc.columns):
        dc = pd.DataFrame({"customer_bk": pd.Series(dtype="object"), "customer_sk": pd.Series(dtype="Int64")})
    else:
        dc = dc[["customer_bk", "customer_sk"]].drop_duplicates()

    dch = dim_channel.copy() if isinstance(dim_channel, pd.DataFrame) else pd.DataFrame()
    if not {"channel_bk","channel_sk"}.issubset(dch.columns):
        dch = pd.DataFrame({"channel_bk": pd.Series(dtype="object"), "channel_sk": pd.Series(dtype="Int64")})
    else:
        dch = dch[["channel_bk", "channel_sk"]].drop_duplicates()

    # Joins
    ws = (ws
          .merge(dc,  on="customer_bk", how="left")
          .merge(dch, on="channel_bk",  how="left")
          .merge(map_start, on="start_key", how="left")
          .merge(map_end,   on="end_key",   how="left")
          )

    # Campos útiles
    if "device" not in ws.columns:
        ws["device"] = pd.NA
    ws["is_ended"] = (~ws["ended_at"].isna()).astype(int)

    # Selección final
    cols = ["session_bk", "customer_sk", "channel_sk", "started_date_sk", "ended_date_sk", "device", "is_ended"]
    for c in cols:
        if c not in ws.columns:
            ws[c] = pd.NA

    return ws[cols]
