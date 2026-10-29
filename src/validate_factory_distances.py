from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
detail_path = root / "data" / "processed" / "factory_destination_distances.csv"
summary_path = root / "reports" / "factory_distance_summary.csv"

df = pd.read_csv(detail_path)
summary = pd.read_csv(summary_path)

print("Rows:", len(df))
print("Unique Row IDs:", df["Row ID"].nunique())
print("Duplicate Row IDs:", df["Row ID"].duplicated().sum())

print("\nMissing values:")
for col in [
    "Factory",
    "Latitude",
    "Longitude",
    "Factory_Latitude",
    "Factory_Longitude",
    "Straight_Line_Distance_KM",
    "Lookup_Status",
]:
    print(f"{col}: {df[col].isna().sum()}")

print("\nDistance checks:")
print("Negative distances:", (df["Straight_Line_Distance_KM"] < 0).sum())
print("Zero distances:", (df["Straight_Line_Distance_KM"] == 0).sum())
print("Maximum distance:", df["Straight_Line_Distance_KM"].max())

print("\nGeocoding status vs distance:")
print(
    df.groupby("Lookup_Status", dropna=False)
      .agg(
          Rows=("Row ID", "count"),
          Mean_KM=("Straight_Line_Distance_KM", "mean"),
          Median_KM=("Straight_Line_Distance_KM", "median"),
      )
      .round(2)
      .to_string()
)

print("\nSaved factory summary:")
print(summary.to_string(index=False))
