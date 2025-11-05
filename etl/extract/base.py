from pathlib import Path
import pandas as pd

RAW_FILES = {
    "address": "address.csv",
    "channel": "channel.csv",
    "customer": "customer.csv",
    "nps_response": "nps_response.csv",
    "payment": "payment.csv",
    "product": "product.csv",
    "product_category": "product_category.csv",
    "province": "province.csv",
    "sales_order": "sales_order.csv",
    "sales_order_item": "sales_order_item.csv",
    "shipment": "shipment.csv",
    "store": "store.csv",
    "web_session": "web_session.csv",
}

def _read_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p, dtype=str).rename(columns=str.lower)

def load_raw_tables(raw_dir: str = "raw") -> dict:
    base = Path(raw_dir)
    dfs = {}
    for name, fname in RAW_FILES.items():
        p = base / fname
        if not p.exists():
            raise FileNotFoundError(f"No se encontró {p}")
        dfs[name] = _read_csv(p)
    return dfs
