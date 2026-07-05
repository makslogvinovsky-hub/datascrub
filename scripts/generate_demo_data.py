"""Generate reproducible demo datasets for DataScrub: a year of company sales
data and a messy product catalog.

Usage:
    python scripts/generate_demo_data.py
"""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

RANDOM_SEED = 42
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"

REGIONS = ["North", "South", "East", "West", "Central"]
SALES_REPS = [
    "Anna Kowalski", "John Smith", "Maria Garcia", "David Chen", "Sophie Muller",
    "James Wilson", "Elena Petrova", "Michael Brown", "Laura Rossi", "Tom Anderson",
]
PRODUCT_CATEGORIES = ["Electronics", "Furniture", "Office Supplies", "Software", "Accessories"]
SUPPLIERS = [
    "Acme Corp", "Globex Industries", "Initech Supplies", "Umbrella Trading",
    "Stark Distribution", "Wayne Logistics", "Hooli Wholesale",
]
PRODUCT_ADJECTIVES = ["Pro", "Lite", "Max", "Mini", "Plus", "Ultra", "Standard"]
PRODUCT_NOUNS = [
    "Desk", "Chair", "Monitor", "Keyboard", "Mouse", "Laptop Stand",
    "Notebook", "Headset", "Cable", "Printer",
]


def generate_sales_data(n_rows: int = 500) -> pd.DataFrame:
    """A year of company sales records with realistic messiness: inconsistent
    region casing/whitespace, missing values, and a few duplicate rows."""
    random.seed(RANDOM_SEED)
    start_date = date(2025, 1, 1)
    rows = []
    for _ in range(n_rows):
        sale_date = start_date + timedelta(days=random.randint(0, 364))
        region = random.choice(REGIONS)
        if random.random() < 0.1:
            region = f" {region.upper()} "
        quantity = random.randint(1, 50)
        unit_price = round(random.uniform(5, 500), 2)
        rows.append({
            "Date": sale_date.isoformat(),
            "Region": region,
            "Sales Rep": random.choice(SALES_REPS),
            "Product Category": random.choice(PRODUCT_CATEGORIES),
            "Quantity": quantity,
            "Revenue": round(quantity * unit_price, 2),
        })

    df = pd.DataFrame(rows)

    for col in ["Region", "Sales Rep", "Revenue"]:
        missing_idx = df.sample(frac=0.03, random_state=RANDOM_SEED).index
        df.loc[missing_idx, col] = None

    dup_rows = df.sample(n=8, random_state=RANDOM_SEED)
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def generate_product_catalog(n_rows: int = 200) -> pd.DataFrame:
    """A product catalog with intentional missing values and duplicate rows."""
    random.seed(RANDOM_SEED + 1)
    rows = []
    for i in range(1, n_rows + 1):
        rows.append({
            "Product ID": f"P{i:04d}",
            "Product Name": f"{random.choice(PRODUCT_ADJECTIVES)} {random.choice(PRODUCT_NOUNS)}",
            "Category": random.choice(PRODUCT_CATEGORIES),
            "Price": round(random.uniform(3, 800), 2),
            "Stock": random.randint(0, 500),
            "Supplier": random.choice(SUPPLIERS),
        })

    df = pd.DataFrame(rows)

    for col in ["Price", "Stock", "Supplier"]:
        missing_idx = df.sample(frac=0.05, random_state=RANDOM_SEED + 1).index
        df.loc[missing_idx, col] = None

    dup_rows = df.sample(n=6, random_state=RANDOM_SEED + 1)
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sales_df = generate_sales_data()
    sales_path = OUTPUT_DIR / "sales_demo.xlsx"
    sales_df.to_excel(sales_path, index=False)
    print(f"Wrote {len(sales_df)} rows to {sales_path}")

    catalog_df = generate_product_catalog()
    catalog_path = OUTPUT_DIR / "product_catalog_dirty.xlsx"
    catalog_df.to_excel(catalog_path, index=False)
    print(f"Wrote {len(catalog_df)} rows to {catalog_path}")


if __name__ == "__main__":
    main()
