
from pathlib import Path
import pandas as pd

# Load the original dataset.
ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "Nassau Candy Distributor.csv"

df = pd.read_csv(CSV_PATH)

print("Dataset loaded:", df.shape)

# Check consistency of information within each order.
columns = [
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Country/Region",
    "City",
    "State/Province",
    "Postal Code",
    "Region",
]

results = []

for column in columns:
    count = (
        df.groupby("Order ID")[column]
        .nunique(dropna=False)
        .gt(1)
        .sum()
    )

    results.append({
        "Column": column,
        "Orders_with_multiple_values": int(count),
    })

print("\n--- ORDER-LEVEL CONSISTENCY AUDIT ---")
print(pd.DataFrame(results).to_string(index=False))

# Official product-to-factory mapping.
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

factories_per_order = df.groupby("Order ID")["Factory"].nunique()

print("\n--- FACTORY DISTRIBUTION PER ORDER ---")
print("Orders involving one factory:",
      int((factories_per_order == 1).sum()))
print("Orders involving multiple factories:",
      int((factories_per_order > 1).sum()))
print("Orders with unmapped factory:",
      int(df.groupby("Order ID")["Factory"].apply(
          lambda values: values.isna().any()
      ).sum()))

print("\nFactory count distribution:")
print(factories_per_order.value_counts().sort_index().to_string())
