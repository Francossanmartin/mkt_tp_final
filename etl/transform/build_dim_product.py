import pandas as pd
from . import make_sk_map, to_datetime, ensure_first_price

def build_dim_category(product_category: pd.DataFrame) -> pd.DataFrame:
    """
    Dimensión de categorías de producto.
    """
    if product_category is None:
        raise ValueError("No se proporcionó la tabla product_category")

    c = product_category.rename(
        columns={
            "category_id": "category_bk",
            "name": "category_name",
            "code": "category_code",
        }
    ).copy()

    sk = make_sk_map(c, "category_bk", "category_sk")
    c = c.merge(sk, on="category_bk", how="left")

    keep = ["category_sk", "category_bk", "category_name", "category_code"]
    for col in keep:
        if col not in c.columns:
            c[col] = pd.NA
    return c[keep].drop_duplicates()


def build_dim_product(product: pd.DataFrame, product_category: pd.DataFrame) -> pd.DataFrame:
    """
    Dimensión de productos (une categoría, asegura first_price y fechas, y crea product_sk).
    """
    if product is None:
        raise ValueError("No se proporcionó la tabla product")
    if product_category is None:
        raise ValueError("No se proporcionó la tabla product_category")

    # Renombres base
    p = product.rename(columns={
        "product_id": "product_bk",
        "category_id": "category_bk"
    }).copy()

    # Asegurar precio estándar y fechas
    p = ensure_first_price(p)
    if "created_at" in p.columns:
        p = to_datetime(p, ["created_at"])

    # Dim categoría y merge
    cat = build_dim_category(product_category)[["category_sk", "category_bk"]]
    p = p.merge(cat, on="category_bk", how="left")

    # SK de producto
    sk = make_sk_map(p, "product_bk", "product_sk")
    p = p.merge(sk, on="product_bk", how="left")

    # Salida estándar (blindada)
    keep = [
        "product_sk",
        "product_bk",
        "sku",
        "name",
        "category_sk",
        "first_price",
        "status",
        "created_at",
    ]
    for col in keep:
        if col not in p.columns:
            p[col] = pd.NA
    return p[keep].drop_duplicates()
