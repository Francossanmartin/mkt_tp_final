import pandas as pd

# =======================================================
# 🔹 make_sk_map → crea surrogate keys (SK) a partir de una BK
# =======================================================
def make_sk_map(df: pd.DataFrame, bk_col: str, sk_col: str) -> pd.DataFrame:
    """
    Genera un mapping de surrogate key incremental a partir de una business key.
    """
    uniques = df[[bk_col]].drop_duplicates().reset_index(drop=True).copy()
    uniques[sk_col] = range(1, len(uniques) + 1)
    return uniques

# =======================================================
# 🔹 to_datetime → convierte columnas a datetime
# =======================================================
def to_datetime(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Convierte las columnas indicadas a tipo datetime (coerce en caso de error).
    """
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

# =======================================================
# 🔹 ensure_first_price → garantiza que exista 'first_price'
# =======================================================
def ensure_first_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Si no existe 'first_price', la crea copiando desde un candidato común.
    Si no hay ninguno, crea la columna con NA.
    """
    if "first_price" in df.columns:
        return df

    for cand in ("unit_price", "price_unitario", "price", "precio_unitario", "monto_unitario"):
        if cand in df.columns:
            out = df.copy()
            out["first_price"] = out[cand]
            return out

    out = df.copy()
    out["first_price"] = pd.NA
    return out
