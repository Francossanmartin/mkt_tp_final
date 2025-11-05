import pandas as pd

def build_fact_order(sales_order: pd.DataFrame, dim_customer: pd.DataFrame,
                     dim_store: pd.DataFrame, dim_channel: pd.DataFrame, dim_date: pd.DataFrame) -> pd.DataFrame:
    # BKs
    so = sales_order.rename(columns={
        "order_id": "order_bk",
        "customer_id": "customer_bk",
        "store_id": "store_bk",
        "channel_id": "channel_bk"
    }).copy()

    # === Mapear fecha a dim_date (sin add_date_key) ===
    if "order_date" in so.columns and "date_key" in dim_date.columns:
        so["order_date"] = pd.to_datetime(so["order_date"], errors="coerce")
        so["order_date_key"] = (
            so["order_date"]
            .dt.strftime("%Y%m%d")
            .pipe(pd.to_numeric, errors="coerce")
            .astype("Int64")
        )
        so = so.merge(
            dim_date[["date_sk", "date_key"]].rename(columns={"date_key": "order_date_key"}),
            on="order_date_key",
            how="left"
        ).rename(columns={"date_sk": "order_date_sk"})
    else:
        so["order_date_sk"] = pd.NA

    # === SKs de dimensiones ===
    so = (
        so.merge(dim_customer[["customer_bk", "customer_sk"]], on="customer_bk", how="left")
          .merge(dim_store[["store_bk", "store_sk"]], on="store_bk", how="left")
          .merge(dim_channel[["channel_bk", "channel_sk"]], on="channel_bk", how="left")
    )

    # === Normalizar montos ===
    for c in ["subtotal_amount", "shipping_fee", "discount_amount", "total_amount"]:
        if c in so.columns:
            so[c] = pd.to_numeric(so[c], errors="coerce").fillna(0)

    # === Selección final ===
    keep = [
        "order_bk", "customer_sk", "store_sk", "channel_sk", "order_date_sk",
        "subtotal_amount", "shipping_fee", "discount_amount", "total_amount",
        "currency_code", "status"
    ]
    for c in keep:
        if c not in so.columns:
            so[c] = pd.NA

    return so[keep]
