
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = ROOT / "data" / "raw" / "Nassau Candy Distributor.csv"
REPORTS_PATH = ROOT / "reports"
PROCESSED_PATH = ROOT / "data" / "processed"

REPORTS_PATH.mkdir(parents=True, exist_ok=True)
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

# Load the original CSV without modifying it.
df = pd.read_csv(CSV_PATH)

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

# Parse dates using the day-month-year format.
for column in ["Order Date", "Ship Date"]:
    df[column + " Parsed"] = pd.to_datetime(
        df[column].astype(str).str.strip(),
        format="%d-%m-%Y",
        errors="coerce"
    )

# Calculate the interval only for auditing.
df["Shipping Lead Time Days"] = (
    df["Ship Date Parsed"] - df["Order Date Parsed"]
).dt.days

lead = df["Shipping Lead Time Days"]

audit = {
    "rows": int(len(df)),
    "columns_in_source": int(len(df.columns) - 3),
    "unique_orders": int(df["Order ID"].nunique()),
    "duplicate_row_ids": int(df["Row ID"].duplicated().sum()),
    "missing_values": {
        str(k): int(v)
        for k, v in df[
            ["Order Date", "Ship Date"]
        ].isna().sum().items()
    },
    "order_date_parse_failures": int(
        df["Order Date Parsed"].isna().sum()
    ),
    "ship_date_parse_failures": int(
        df["Ship Date Parsed"].isna().sum()
    ),
    "order_date_min": str(df["Order Date Parsed"].min()),
    "order_date_max": str(df["Order Date Parsed"].max()),
    "ship_date_min": str(df["Ship Date Parsed"].min()),
    "ship_date_max": str(df["Ship Date Parsed"].max()),
    "lead_time_min_days": (
        int(lead.min()) if lead.notna().any() else None
    ),
    "lead_time_median_days": (
        float(lead.median()) if lead.notna().any() else None
    ),
    "lead_time_max_days": (
        int(lead.max()) if lead.notna().any() else None
    ),
    "negative_lead_times": int((lead < 0).sum()),
}

# Save the audit report.
audit_file = REPORTS_PATH / "data_quality_audit.json"

with open(audit_file, "w", encoding="utf-8") as file:
    json.dump(audit, file, indent=2)

# Preserve parsed dates and calculated intervals for investigation.
output_file = (
    PROCESSED_PATH / "nassau_shipping_audited.csv"
)
df.to_csv(output_file, index=False)

print("\nDATA QUALITY AUDIT")
print(json.dumps(audit, indent=2))

print("\nAudit saved to:", audit_file)
print("Audited data saved to:", output_file)

print(
    "\nWARNING: Do not publish route-efficiency rankings "
    "until the date anomaly is explained."
)

# Investigate suspicious dates without changing the source data.
print("\n--- DATE ANOMALY INVESTIGATION ---")

columns_to_show = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "City",
    "Product Name",
    "Shipping Lead Time Days",
]

print("\nFirst 10 records:")
print(df[columns_to_show].head(10).to_string(index=False))

print("\nLast 10 records:")
print(df[columns_to_show].tail(10).to_string(index=False))

print("\nOrder ID examples:")
print(df["Order ID"].head(20).to_list())

print("\nOrder ID prefix counts:")
order_prefix = df["Order ID"].astype(str).str[:4]
print(order_prefix.value_counts().sort_index().to_string())

print("\nOrder date counts by year:")
print(
    df["Order Date Parsed"]
    .dt.year
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nShip date counts by year:")
print(
    df["Ship Date Parsed"]
    .dt.year
    .value_counts()
    .sort_index()
    .to_string()
)

# Validate the supplied product-to-factory mapping.
print("\n--- FACTORY MAPPING VALIDATION ---")

product_to_factory = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Kazookles": "The Other Factory",
}

df["Factory"] = df["Product Name"].map(product_to_factory)

unmapped = sorted(
    df.loc[df["Factory"].isna(), "Product Name"]
    .dropna()
    .unique()
)

print("Unique products in dataset:", df["Product Name"].nunique())
print("Products in mapping:", len(product_to_factory))
print("Rows without a factory:", int(df["Factory"].isna().sum()))

if unmapped:
    print("Products requiring mapping:")
    for product in unmapped:
        print("-", repr(product))
else:
    print("All product names match the supplied mapping.")

print("\nOrder volume by assigned factory:")
print(
    df.groupby("Factory")["Order ID"]
    .nunique()
    .sort_values(ascending=False)
    .to_string()
)
