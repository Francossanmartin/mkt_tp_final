import pandas as pd
from . import make_sk_map, to_datetime

def build_dim_customer(customer: pd.DataFrame, address: pd.DataFrame, province: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la dimensión de clientes sin unión con address ni province.
    Se generan claves surrogate y se formatean fechas.
    """
    # Copia de seguridad y normalización de columnas
    c = customer.rename(columns={"customer_id": "customer_bk"}).copy()

    # Convertir fecha de creación si existe
    if "created_at" in c.columns:
        c = to_datetime(c, ["created_at"])

    # Crear surrogate key (customer_sk)
    sk = make_sk_map(c, "customer_bk", "customer_sk")
    c = c.merge(sk, on="customer_bk", how="left")

    # Mantener solo las columnas relevantes
    keep = [
        "customer_sk",
        "customer_bk",
        "email",
        "first_name",
        "last_name",
        "status",
        "created_at"
    ]

    # Crear columnas vacías si alguna falta (por seguridad)
    for col in keep:
        if col not in c.columns:
            c[col] = pd.NA

    # Devolver dataframe limpio y sin duplicados
    return c[keep].drop_duplicates()

