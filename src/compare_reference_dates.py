from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent

local = pd.read_csv(root / "data/raw/Nassau Candy Distributor.csv")
reference = pd.read_csv(root / "data/raw/public_reference.csv")

columns = ["Row ID", "Order ID", "Order Date", "Ship Date"]

for name, df in [("Local", local), ("Reference", reference)]:
    df["Row ID"] = pd.to_numeric(df["Row ID"], errors="raise")

local = local[columns].rename(columns={
    "Order Date": "Local_Order_Date",
    "Ship Date": "Local_Ship_Date",
})

reference = reference[columns].rename(columns={
    "Order Date": "Reference_Order_Date",
    "Ship Date": "Reference_Ship_Date",
})

merged = local.merge(
    reference,
    on=["Row ID", "Order ID"],
    how="outer",
    indicator=True,
    validate="one_to_one",
)

print("Local rows:", len(local))
print("Reference rows:", len(reference))
print("\nMatching status:")
print(merged["_merge"].value_counts().to_string())

matched = merged[merged["_merge"] == "both"]

order_diff = (
    matched["Local_Order_Date"] != matched["Reference_Order_Date"]
)
ship_diff = (
    matched["Local_Ship_Date"] != matched["Reference_Ship_Date"]
)

print("\nMatched records:", len(matched))
print("Order dates differing:", int(order_diff.sum()))
print("Ship dates differing:", int(ship_diff.sum()))

print("\nExamples of date differences:")
print(
    matched.loc[
        order_diff | ship_diff,
        [
            "Row ID",
            "Order ID",
            "Local_Order_Date",
            "Reference_Order_Date",
            "Local_Ship_Date",
            "Reference_Ship_Date",
        ],
    ].head(15).to_string(index=False)
)