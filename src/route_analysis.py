
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "nassau_shipping_audited.csv"

df = pd.read_csv(DATA_PATH)

# Inspect distinct customer destinations
destination_columns = [
    "Country/Region",
    "State/Province",
    "City",
    "Postal Code",
]

destinations = (
    df[destination_columns]
    .drop_duplicates()
    .sort_values(["Country/Region", "State/Province", "City"])
)

print("Unique city/state/postal-code combinations:", len(destinations))

print("\nFirst 30 destinations:")
print(destinations.head(30).to_string(index=False))

print("\nMissing destination fields:")
print(df[destination_columns].isna().sum())

print("\nPostal code examples by country:")
for country, group in df.groupby("Country/Region"):
    print(f"\n{country}:")
    print(group["Postal Code"].dropna().astype(str).head(10).tolist())

# Save the unique destinations for coordinate lookup
output_path = ROOT / "data" / "processed" / "unique_destinations.csv"
destinations.to_csv(output_path, index=False)

print(f"\nSaved destination list to: {output_path}")


print("\n--- DESTINATION UNIQUENESS CHECK ---")

print(
    "Unique city/state/country combinations:",
    df[["Country/Region", "State/Province", "City"]]
    .drop_duplicates()
    .shape[0],
)

print(
    "Unique city/state/postal-code/country combinations:",
    df[["Country/Region", "State/Province", "City", "Postal Code"]]
    .drop_duplicates()
    .shape[0],
)

postal_city_counts = (
    df[["Country/Region", "Postal Code", "City", "State/Province"]]
    .drop_duplicates()
    .groupby(["Country/Region", "Postal Code"])
    .size()
)

print(
    "Postal codes associated with multiple city/state combinations:",
    int((postal_city_counts > 1).sum()),
)

print("\nSample destination combinations:")
print(
    df[["Country/Region", "State/Province", "City", "Postal Code"]]
    .drop_duplicates()
    .head(10)
    .to_string(index=False)
)
