
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "reports" / "factory_state_routes_all.csv"
REPORTS = ROOT / "reports"

df = pd.read_csv(INPUT)

required = [
    "Factory",
    "Country/Region",
    "State/Province",
    "Unique_Orders",
    "Mean_Distance_KM",
    "Median_Distance_KM",
    "Geographic_Usable_Percent",
]

if not set(required).issubset(df.columns):
    raise ValueError("Required columns are missing.")

for threshold in [10, 30]:
    eligible = df[df["Unique_Orders"] >= threshold].copy()

    shortest = eligible.nsmallest(10, "Mean_Distance_KM")
    longest = eligible.nlargest(10, "Mean_Distance_KM")

    shortest["Ranking"] = range(1, len(shortest) + 1)
    longest["Ranking"] = range(1, len(longest) + 1)

    shortest["Distance_Ranking"] = "Shortest"
    longest["Distance_Ranking"] = "Longest"

    combined = pd.concat([shortest, longest], ignore_index=True)

    output = REPORTS / f"state_distance_rankings_min_{threshold}_orders.csv"
    combined.to_csv(output, index=False)

    print(f"\nMINIMUM {threshold} ORDERS")
    print("=" * 45)
    print("Eligible routes:", len(eligible))

    print("\n10 shortest mean-distance routes:")
    print(
        shortest[
            ["Ranking", "Factory", "Country/Region",
             "State/Province", "Unique_Orders", "Mean_Distance_KM"]
        ].round(2).to_string(index=False)
    )

    print("\n10 longest mean-distance routes:")
    print(
        longest[
            ["Ranking", "Factory", "Country/Region",
             "State/Province", "Unique_Orders", "Mean_Distance_KM"]
        ].round(2).to_string(index=False)
    )

    print("\nSaved:", output)

print("\nInterpretation:")
print("These are geographic distance rankings, not delivery-speed rankings.")
