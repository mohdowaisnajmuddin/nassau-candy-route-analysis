
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "factory_destination_distances.csv"
OUTPUT = ROOT / "reports" / "distance_confidence_summary.csv"

df = pd.read_csv(INPUT)

# Preserve the original geocoding status and group results by it.
summary = (
    df.groupby("Lookup_Status", dropna=False)
    .agg(
        Order_Lines=("Row ID", "count"),
        Distinct_Orders=("Order ID", "nunique"),
        Distinct_Destinations=("City", "nunique"),
        Mean_Distance_KM=("Straight_Line_Distance_KM", "mean"),
        Median_Distance_KM=("Straight_Line_Distance_KM", "median"),
        Max_Distance_KM=("Straight_Line_Distance_KM", "max"),
    )
    .reset_index()
)

summary["Share_of_Order_Lines_Pct"] = (
    summary["Order_Lines"] / len(df) * 100
)

summary = summary.round(2)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
summary.to_csv(OUTPUT, index=False)

print("Total order lines:", len(df))
print("\nDistance summary by geocoding status:")
print(summary.to_string(index=False))

print("\nSaved:", OUTPUT)
print(
    "\nInterpretation note: status groups describe geocoding provenance, "
    "not independently measured coordinate accuracy."
)
