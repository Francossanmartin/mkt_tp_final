from pathlib import Path
import pandas as pd

# ========== EXTRACT ==========
from etl.extract.base import load_raw_tables

# ========== TRANSFORM (dims) ==========
from etl.transform.build_dim_channel import build_dim_channel
from etl.transform.build_dim_product import build_dim_product
from etl.transform.build_dim_customer import build_dim_customer
from etl.transform.build_dim_location import build_dim_location
from etl.transform.build_dim_store import build_dim_store
from etl.transform.build_dim_date import build_dim_date
from etl.transform import ensure_first_price

# ========== TRANSFORM (facts) ==========
from etl.transform.build_fact_nps_response import build_fact_nps_response
from etl.transform.build_fact_order_item import build_fact_order_item
from etl.transform.build_fact_order import build_fact_order
from etl.transform.build_fact_payment import build_fact_payment
from etl.transform.build_fact_shipment import build_fact_shipment
from etl.transform.build_fact_web_session import build_fact_web_session

# ========== RUTAS ==========
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR  = BASE_DIR / "raw"
DW_DIR   = BASE_DIR / "data warehouse"

# ========== HELPERS ==========
def save_dw(tables: dict, out_dir: Path, tag: str = ""):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        if isinstance(df, pd.DataFrame):
            df.to_csv(out_dir / f"{name}.csv", index=False)
            print(f"[DW]{tag} {name}.csv ({len(df)} filas)")

def normalize_prices(raw: dict):
    price_cols = {"first_price","unit_price","price_unitario","price","precio_unitario","monto_unitario"}
    for k, df in list(raw.items()):
        if isinstance(df, pd.DataFrame) and any(c in df.columns for c in price_cols):
            try: raw[k] = ensure_first_price(df)
            except: pass

def add_aliases(raw: dict):
    for k in ("web_sessions","websession","sessions","session"):
        if k in raw and "web_session" not in raw:
            raw["web_session"] = raw[k]

def build_steps(raw: dict, dims: dict):
    """Devuelve dos listas de (nombre, callable) para construir dims y facts."""
    dim_steps = [
        ("dim_channel",  lambda: build_dim_channel(raw["channel"])) if "channel" in raw else None,
        ("dim_product",  lambda: build_dim_product(raw["product"], raw["product_category"]))
            if {"product","product_category"} <= raw.keys() else None,
        ("dim_customer", lambda: build_dim_customer(raw["customer"], raw.get("address"), raw.get("province")))
            if "customer" in raw else None,
        ("dim_location", lambda: build_dim_location(raw["address"], raw["province"]))
            if {"address","province"} <= raw.keys() else None,
        ("dim_store",    lambda: build_dim_store(raw["store"], raw["address"], raw["province"]))
            if {"store","address","province"} <= raw.keys() else None,
        ("dim_date",     lambda: build_dim_date(
            raw.get("sales_order",  pd.DataFrame({"order_date": []})),
            raw.get("shipment",     pd.DataFrame({"shipped_at": [], "delivered_at": []})),
            raw.get("payment",      pd.DataFrame({"paid_at": []}))
        )),
    ]
    dim_steps = [s for s in dim_steps if s is not None]

    fact_steps = [
        ("fact_sales_order_item", lambda: build_fact_order_item(raw["sales_order_item"], raw["product"]))
            if {"sales_order_item","product"} <= raw.keys() else None,
        ("fact_order", lambda: build_fact_order(
            raw["sales_order"], dims["dim_customer"], dims["dim_store"], dims["dim_channel"], dims["dim_date"]
        )) if "sales_order" in raw and {"dim_customer","dim_store","dim_channel","dim_date"} <= dims.keys() else None,
        ("fact_payment", lambda: build_fact_payment(raw["payment"], raw.get("sales_order"), dims["dim_date"]))
            if "payment" in raw and "dim_date" in dims else None,
        ("fact_shipment", lambda: build_fact_shipment(raw["shipment"], dims["dim_date"]))
            if "shipment" in raw and "dim_date" in dims else None,
        ("fact_web_session", lambda: build_fact_web_session(
            raw["web_session"], dims["dim_customer"], dims["dim_channel"], dims["dim_date"]
        )) if "web_session" in raw and {"dim_customer","dim_channel","dim_date"} <= dims.keys() else None,
        ("fact_nps_response", lambda: build_fact_nps_response(
            raw["nps_response"], dims["dim_customer"], dims["dim_channel"], dims["dim_date"]
        )) if "nps_response" in raw and {"dim_customer","dim_channel","dim_date"} <= dims.keys() else None,
    ]
    fact_steps = [s for s in fact_steps if s is not None]
    return dim_steps, fact_steps

# ========== PIPELINE ==========
def run(raw_dir: Path = RAW_DIR, dw_dir: Path = DW_DIR):
    raw = load_raw_tables(raw_dir)
    add_aliases(raw)
    normalize_prices(raw)

    # --- DIMs ---
    dims, facts = {}, {}
    dim_steps, fact_steps = build_steps(raw, dims)

    for name, fn in dim_steps:
        try:
            df = fn()
            if isinstance(df, pd.DataFrame) and not df.empty:
                dims[name] = df
                print(f"[DIM] {name} OK ({len(df)})")
        except Exception as e:
            print(f"[DIM] {name} ERROR: {e}")

    save_dw(dims, dw_dir, tag=" (DIM)")

    # --- FACTs ---
    # reconstruyo steps ahora que ya existen dims
    _, fact_steps = build_steps(raw, dims)
    for name, fn in fact_steps:
        try:
            df = fn()
            if isinstance(df, pd.DataFrame) and not df.empty:
                facts[name] = df
                print(f"[FACT] {name} OK ({len(df)})")
        except Exception as e:
            print(f"[FACT] {name} ERROR: {e}")

    save_dw(facts, dw_dir, tag=" (FACT)")
    print("[OK] ETL finalizado.")

if __name__ == "__main__":
    run()
