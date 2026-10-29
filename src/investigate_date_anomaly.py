
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = ROOT / "data" / "raw" / "Nassau Candy Distributor.csv"

if not CSV_FILE.exists():
    raise FileNotFoundError(f"Source CSV not found: {CSV_FILE}")

df = pd.read_csv(CSV_FILE)

required = ["Order ID", "Order Date", "Ship Date"]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(
        f"Missing columns: {missing}\n"
        f"Available columns: {df.columns.tolist()}"
    )

print("\n========== SOURCE DATA ==========")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Original columns: {df.columns.tolist()}")

# Parse copies of the date columns, preserving the original data.
for col in ["Order Date", "Ship Date"]:
    df[f"{col}_parsed"] = pd.to_datetime(
        df[col],
        format="%d-%m-%Y",
        errors="coerce",
    )

print("\n========== DATE RANGES ==========")

for col in ["Order Date", "Ship Date"]:
    parsed = df[f"{col}_parsed"]
    print(f"\n{col}")
    print(f"Minimum: {parsed.min()}")
    print(f"Maximum: {parsed.max()}")
    print(f"Unparsed values: {parsed.isna().sum():,}")

df["Date_Difference_Days"] = (
    df["Ship Date_parsed"] - df["Order Date_parsed"]
).dt.days

print("\n========== DATE DIFFERENCES ==========")
print(df["Date_Difference_Days"].describe().to_string())

print("\nNegative differences:")
print((df["Date_Difference_Days"] < 0).sum())

print("\nZero-day differences:")
print((df["Date_Difference_Days"] == 0).sum())

print("\nDifferences greater than 365 days:")
print((df["Date_Difference_Days"] > 365).sum())

print("\n========== ORDER ID PATTERNS ==========")
print(
    df["Order ID"]
    .astype(str)
    .str.extract(r"^([A-Za-z]+-\d{4})", expand=False)
    .value_counts(dropna=False)
    .head(20)
    .to_string()
)

print("\n========== EARLIEST SHIP DATES ==========")
print(
    df.sort_values("Ship Date_parsed")[
        ["Order ID", "Order Date", "Ship Date",
         "Order Date_parsed", "Ship Date_parsed",
         "Date_Difference_Days"]
    ].head(10).to_string(index=False)
)

print("\n========== LATEST SHIP DATES ==========")
print(
    df.sort_values("Ship Date_parsed", ascending=False)[
        ["Order ID", "Order Date", "Ship Date",
         "Order Date_parsed", "Ship Date_parsed",
         "Date_Difference_Days"]
    ].head(10).to_string(index=False)
)

print("\n========== ORIGINAL DATA PRESERVED ==========")
print("This script only reads the CSV and creates in-memory columns.")
print("It does not modify or overwrite the source file.")


# --------------------------------------------------
# Further investigation: identify date patterns
# --------------------------------------------------

print("\n========== ORDER ID YEAR VS ORDER DATE YEAR ==========")

df["Order_ID_Year"] = pd.to_numeric(
    df["Order ID"]
    .astype(str)
    .str.extract(r"^[A-Za-z]+-(\d{4})", expand=False),
    errors="coerce",
)

df["Order_Date_Year"] = df["Order Date_parsed"].dt.year
df["Ship_Date_Year"] = df["Ship Date_parsed"].dt.year

print(
    df.groupby(
        ["Order_ID_Year", "Order_Date_Year", "Ship_Date_Year"],
        dropna=False,
    )
    .size()
    .rename("Record_Count")
    .reset_index()
    .sort_values(
        ["Order_ID_Year", "Order_Date_Year", "Ship_Date_Year"]
    )
    .to_string(index=False)
)

print("\n========== DATE DIFFERENCE BY ORDER ID YEAR ==========")

print(
    df.groupby("Order_ID_Year")["Date_Difference_Days"]
    .agg(["count", "min", "median", "mean", "max"])
    .round(2)
    .to_string()
)

print("\n========== MOST COMMON EXACT DATE DIFFERENCES ==========")

print(
    df["Date_Difference_Days"]
    .value_counts()
    .head(15)
    .rename_axis("Difference_Days")
    .reset_index(name="Record_Count")
    .to_string(index=False)
)

print("\n========== DATE DIFFERENCE BY SHIP MODE ==========")

if "Ship Mode" in df.columns:
    print(
        df.groupby("Ship Mode")["Date_Difference_Days"]
        .agg(["count", "min", "median", "mean", "max"])
        .round(2)
        .to_string()
    )

print("\n========== DATE DIFFERENCE BY ORDER DATE YEAR ==========")

print(
    df.groupby("Order_Date_Year")["Date_Difference_Days"]
    .agg(["count", "min", "median", "mean", "max"])
    .round(2)
    .to_string()
)

print("\n========== INVESTIGATION COMPLETE ==========")
print("No source dates were changed.")


# --------------------------------------------------
# Investigate date consistency within each order
# --------------------------------------------------

print("\n========== DATE CONSISTENCY WITHIN ORDERS ==========")

order_consistency = (
    df.groupby("Order ID", dropna=False)
    .agg(
        Product_Rows=("Row ID", "size"),
        Unique_Order_Dates=("Order Date_parsed", "nunique"),
        Unique_Ship_Dates=("Ship Date_parsed", "nunique"),
        Order_Date=("Order Date_parsed", "first"),
        Ship_Date=("Ship Date_parsed", "first"),
        Order_ID_Year=("Order_ID_Year", "first"),
    )
    .reset_index()
)

print(f"Unique orders: {len(order_consistency):,}")

print(
    "Orders with multiple order dates:",
    int((order_consistency["Unique_Order_Dates"] > 1).sum()),
)

print(
    "Orders with multiple ship dates:",
    int((order_consistency["Unique_Ship_Dates"] > 1).sum()),
)

print("\n========== ORDER DATE SPREAD BY ID YEAR ==========")

for year in sorted(
    order_consistency["Order_ID_Year"].dropna().unique()
):
    group = order_consistency[
        order_consistency["Order_ID_Year"] == year
    ]

    print(f"\nOrder ID year: {int(year)}")
    print(f"Distinct orders: {len(group):,}")
    print(
        "Distinct order dates:",
        group["Order_Date"].nunique(),
    )
    print(
        "Distinct ship dates:",
        group["Ship_Date"].nunique(),
    )
    print(
        "Order date range:",
        group["Order_Date"].min(),
        "to",
        group["Order_Date"].max(),
    )
    print(
        "Ship date range:",
        group["Ship_Date"].min(),
        "to",
        group["Ship_Date"].max(),
    )

print("\n========== SAMPLE ORDERS BY ID YEAR ==========")

for year in sorted(
    order_consistency["Order_ID_Year"].dropna().unique()
):
    print(f"\n--- Order ID year {int(year)} ---")

    print(
        order_consistency[
            order_consistency["Order_ID_Year"] == year
        ][
            [
                "Order ID",
                "Product_Rows",
                "Order_Date",
                "Ship_Date",
            ]
        ]
        .sort_values("Order_Date")
        .head(5)
        .to_string(index=False)
    )

print("\nSource CSV remains unchanged.")
