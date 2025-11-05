import pandas as pd

# --- make_sk_map: crea SKs incrementales a partir de una BK ---
def make_sk_map(df, bk_col, sk_col):
    # df: DataFrame con al menos bk_col
    uniques = df[[bk_col]].drop_duplicates().reset_index(drop=True).copy()
    uniques[sk_col] = range(1, len(uniques) + 1)
    return uniques

# --- to_datetime: convierte columnas a datetime (ignora errores) ---
def to_datetime(df, columns):
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    return out

# --- ensure_first_price: garantiza que exista 'first_price' ---
def ensure_first_price(df):
    if "first_price" in df.columns:
        return df
    out = df.copy()
    for cand in ("unit_price", "price_unitario", "price", "precio_unitario", "monto_unitario"):
        if cand in out.columns:
            out["first_price"] = out[cand]
            return out
    out["first_price"] = pd.NA
    return out


