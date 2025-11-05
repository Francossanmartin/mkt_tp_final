import pandas as pd
from . import make_sk_map, to_datetime

def build_dim_store(store: pd.DataFrame, address: pd.DataFrame, province: pd.DataFrame) -> pd.DataFrame:
    if store is None:
        raise ValueError("No se proporcionó la tabla store")
    if address is None:
        raise ValueError("No se proporcionó la tabla address")
    if province is None:
        raise ValueError("No se proporcionó la tabla province")

    # Copias y renombres base
    s = store.rename(columns={
        "store_id": "store_bk",
        "name": "store_name",
        "code": "store_code",
        "created_at": "created_at_store",
        "status": "status"
    }).copy()

    addr = address.rename(columns={
        "address_id": "address_bk",
        "province_id": "province_bk"
    }).copy()

    prov = province.rename(columns={
        "province_id": "province_bk",
        "name": "province_name",
        "code": "province_code"
    }).copy()

    # Fecha si existe
    if "created_at_store" in s.columns:
        s = to_datetime(s, ["created_at_store"])

    # Detectar la FK de address en store
    addr_fk_candidates = ["address_id", "address_bk", "address_fk", "id_address"]
    addr_fk = next((c for c in addr_fk_candidates if c in s.columns), None)
    if addr_fk is None:
        # si la tienda no tiene FK a address, seguimos sin enriquecer ubicación
        d = s.copy()
        d["city"] = pd.NA
        d["province_bk"] = pd.NA
        d["province_name"] = pd.NA
        d["province_code"] = pd.NA
        d["postal_code"] = pd.NA
        d["country_code"] = pd.NA
    else:
        # Unir con address y luego con province
        d = s.merge(addr, left_on=addr_fk, right_on="address_bk", how="left") \
             .merge(prov, on="province_bk", how="left")

    # Crear SK de store
    sk = make_sk_map(d, "store_bk", "store_sk")
    d = d.merge(sk, on="store_bk", how="left")

    # Selección final blindada
    keep = [
        "store_sk", "store_bk", "store_name", "store_code",
        "city", "province_name", "province_code", "postal_code",
        "country_code", "status", "created_at_store"
    ]
    for col in keep:
        if col not in d.columns:
            d[col] = pd.NA

    return d[keep].drop_duplicates()
