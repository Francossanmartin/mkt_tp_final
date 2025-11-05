import pandas as pd

def build_fact_payment(payment: pd.DataFrame, sales_order: pd.DataFrame, dim_date: pd.DataFrame) -> pd.DataFrame:
    # Renombrar BK
    p = payment.rename(columns={"order_id": "order_bk"}).copy()

    # === Mapear fecha a dim_date ===
    if "paid_at" in p.columns and "date_key" in dim_date.columns:
        p["paid_at"] = pd.to_datetime(p["paid_at"], errors="coerce")
        p["paid_date_key"] = (
            p["paid_at"]
            .dt.strftime("%Y%m%d")
            .pipe(pd.to_numeric, errors="coerce")
            .astype("Int64")
        )

        p = p.merge(
            dim_date[["date_sk", "date_key"]].rename(columns={"date_key": "paid_date_key"}),
            on="paid_date_key",
            how="left"
        ).rename(columns={"date_sk": "paid_date_sk"})
    else:
        p["paid_date_sk"] = pd.NA

    # === Normalizar monto ===
    p["amount"] = pd.to_numeric(p.get("amount", 0), errors="coerce").fillna(0)

    # === Columnas finales ===
    keep = ["order_bk", "paid_date_sk", "status", "payment_method", "amount", "transaction_ref"]
    for c in keep:
        if c not in p.columns:
            p[c] = pd.NA

    return p[keep]
