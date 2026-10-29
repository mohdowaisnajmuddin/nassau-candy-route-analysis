
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "factory_destination_distances.csv"
REPORTS = ROOT / "reports"

FACTORY_OUT = REPORTS / "factory_analysis.csv"
DESTINATION_OUT = REPORTS / "destination_analysis.csv"
QUALITY_OUT = REPORTS / "analysis_quality_summary.csv"


def main():
    df = pd.read_csv(INPUT)

    required = [
        "Row ID",
        "Order ID",
        "Country/Region",
        "State/Province",
        "City",
        "Postal Code",
        "Factory",
        "Lookup_Status",
        "Straight_Line_Distance_KM",
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    REPORTS.mkdir(parents=True, exist_ok=True)

    # 1. Factory-level analysis.
    factory_summary = (
        df.groupby("Factory", dropna=False)
        .agg(
            Order_Lines=("Row ID", "count"),
            Distinct_Orders=("Order ID", "nunique"),
            Mean_Straight_Line_KM=("Straight_Line_Distance_KM", "mean"),
            Median_Straight_Line_KM=("Straight_Line_Distance_KM", "median"),
            Maximum_Straight_Line_KM=("Straight_Line_Distance_KM", "max"),
        )
        .reset_index()
        .round(2)
    )
    factory_summary.to_csv(FACTORY_OUT, index=False)

    # 2. Destination and factory analysis.
    # Postal code is retained as a string so leading zeros are preserved.
    destination_summary = (
        df.groupby(
            [
                "Country/Region",
                "State/Province",
                "City",
                "Postal Code",
                "Factory",
                "Lookup_Status",
            ],
            dropna=False,
        )
        .agg(
            Order_Lines=("Row ID", "count"),
            Distinct_Orders=("Order ID", "nunique"),
            Mean_Straight_Line_KM=("Straight_Line_Distance_KM", "mean"),
            Median_Straight_Line_KM=("Straight_Line_Distance_KM", "median"),
            Maximum_Straight_Line_KM=("Straight_Line_Distance_KM", "max"),
        )
        .reset_index()
        .round(2)
        .sort_values(
            ["Mean_Straight_Line_KM"],
            ascending=False,
        )
    )
    destination_summary.to_csv(DESTINATION_OUT, index=False)

    # 3. Quality summary by geocoding status.
    quality_summary = (
        df.groupby("Lookup_Status", dropna=False)
        .agg(
            Order_Lines=("Row ID", "count"),
            Distinct_Orders=("Order ID", "nunique"),
            Mean_Straight_Line_KM=("Straight_Line_Distance_KM", "mean"),
            Median_Straight_Line_KM=("Straight_Line_Distance_KM", "median"),
            Missing_Distances=("Straight_Line_Distance_KM",
                               lambda s: int(s.isna().sum())),
        )
        .reset_index()
    )

    quality_summary["Share_of_Order_Lines_Pct"] = (
        quality_summary["Order_Lines"] / len(df) * 100
    )
    quality_summary = quality_summary.round(2)
    quality_summary.to_csv(QUALITY_OUT, index=False)

    print("Total source rows:", len(df))
    print("Unique Row IDs:", df["Row ID"].nunique())
    print("Factory groups:", df["Factory"].nunique())
    print("Destination/factory/status groups:", len(destination_summary))

    print("\nFactory analysis:")
    print(factory_summary.to_string(index=False))

    print("\nTen longest estimated destination/factory distances:")
    print(
        destination_summary[
            [
                "City",
                "State/Province",
                "Postal Code",
                "Factory",
                "Lookup_Status",
                "Order_Lines",
                "Mean_Straight_Line_KM",
            ]
        ].head(10).to_string(index=False)
    )

    print("\nQuality summary:")
    print(quality_summary.to_string(index=False))

    print("\nSaved reports:")
    print(FACTORY_OUT)
    print(DESTINATION_OUT)
    print(QUALITY_OUT)

    print(
        "\nLimitations: straight-line distance is not road distance. "
        "Coordinates have not been independently verified. "
        "Order/ship-date anomalies remain unresolved."
    )


if __name__ == "__main__":
    main()
