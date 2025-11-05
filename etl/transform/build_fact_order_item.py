import pandas as pd
from . import to_datetime

def build_fact_order_item(order_item: pd.DataFrame, product: pd.DataFrame) -> pd.DataFrame:
    """
    Tabla de hechos de ítems de pedido (Fact_Order_Item)
    Blindada: nunca falla por 'first_price' faltante.
    """

    oi = order_item.copy()
    pr = product.copy()

    # Normalizar nombres de columnas
    oi = oi.rename(columns={
        "order_item_id": "order_item_bk",
        "sales_order_id": "sales_order_bk",
        "product_id": "product_bk",
    })
    pr = pr.rename(columns={"product_id": "product_bk"})

    # Merge con producto (por si queremos info adicional)
    f = oi.merge(pr, on="product_bk", how="left", suffixes=("", "_pr"))

    # Buscar columna de precio y estandarizar a 'first_price'
    price_candidates = ["first_price", "unit_price", "price_unitario", "price"]
    found_price = None
    for col in price_candidates:
        if col in f.columns:
            found_price = col
            break

    if found_price:
        f["first_price"] = f[found_price]
    else:
        f["first_price"] = pd.NA  # columna vacía si no hay ninguna

    # Buscar columna de cantidad
    qty_candidates = ["quantity", "qty", "cantidad", "quantity_ordered"]
    found_qty = None
    for col in qty_candidates:
        if col in f.columns:
            found_qty = col
            break

    if found_qty:
        f["quantity"] = f[found_qty]
    else:
        f["quantity"] = pd.NA

    # Calcular importe total si ambas columnas existen numéricamente
    try:
        f["total_amount"] = f["quantity"].astype(float) * f["first_price"].astype(float)
    except Exception:
        f["total_amount"] = pd.NA

    # Agregar surrogate key
    f["fact_order_item_sk"] = range(1, len(f) + 1)

    # Mantener columnas importantes (rellena si falta alguna)
    keep = [
        "fact_order_item_sk",
        "order_item_bk",
        "sales_order_bk",
        "product_bk",
        "quantity",
        "first_price",
        "total_amount"
    ]

    for col in keep:
        if col not in f.columns:
            f[col] = pd.NA

    return f[keep].drop_duplicates()


