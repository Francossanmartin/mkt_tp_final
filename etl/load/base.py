from pathlib import Path

def write_table(df, name: str, dw_dir: str = "data warehouse"):
    d = Path(dw_dir); d.mkdir(parents=True, exist_ok=True)
    df.to_csv(d / f"{name}.csv", index=False)

def write_many(tables: dict, dw_dir: str = "data warehouse"):
    for name, df in tables.items():
        write_table(df, name, dw_dir)
