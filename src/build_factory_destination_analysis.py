
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "factory_destination_distances.csv"
REPORTS = ROOT / "reports"

ROUTE_OUT = REPORTS / "factory_destination_route_analysis.csv"
SUMMARY_OUT = REPORTS / "route_analysis_summary.csv"


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

    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert distance to numeric without changing the source CSV.
    df["Straight_Line_Distance_KM"] = pd.to_numeric(
        df["Straight_Line_Distance_KM"],
        errors="coerce",
    )

    REPORTS.mkdir(parents=True, exist_ok=True)

        # One record per order for distance calculations.
    # Order consistency has been audited separately.
    order_df = df.drop_duplicates(
        subset=["Order ID"]
    ).copy()

    # One group for each factory-to-destination combination.
    route_columns = [
        "Factory",
        "Country/Region",
        "State/Province",
        "City",
        "Postal Code",
    ]

        # Product-line counts from the original dataset.
    route_line_counts = (
        df.groupby(route_columns, dropna=False)
        .agg(
            Order_Lines=("Row ID", "count"),
        )
        .reset_index()
    )

    # Order counts and distance statistics from unique orders.
    route_order_stats = (
        order_df.groupby(route_columns, dropna=False)
        .agg(
            Distinct_Orders=("Order ID", "nunique"),
            Mean_Estimated_Distance_KM=(
                "Straight_Line_Distance_KM", "mean"
            ),
            Median_Estimated_Distance_KM=(
                "Straight_Line_Distance_KM", "median"
            ),
            Maximum_Estimated_Distance_KM=(
                "Straight_Line_Distance_KM", "max"
            ),
            Missing_Distance_Rows=(
                "Straight_Line_Distance_KM",
                lambda values: int(values.isna().sum()),
            ),
        )
        .reset_index()
    )

    # Combine both summaries at factory-destination level.
    routes = route_line_counts.merge(
        route_order_stats,
        on=route_columns,
        how="left",
        validate="one_to_one",
    )

    # Add geocoding-status counts for each factory/destination.

    status_counts = (
        order_df.assign(
            Lookup_Status=order_df["Lookup_Status"].fillna(
                "Missing status"
            )
        )
        .pivot_table(
            index=route_columns,
            columns="Lookup_Status",
            values="Order ID",
            aggfunc="nunique",
            fill_value=0,
        )
        .reset_index()
    )

    # Make status-count column names explicit.
    status_counts.columns = [
        str(column)
        if column in route_columns
        else f"Status_Count_{column}"
        for column in status_counts.columns
    ]

    routes = routes.merge(
        status_counts,
        on=route_columns,
        how="left",
        validate="one_to_one",
    )

    routes = routes.sort_values(
        ["Order_Lines", "Mean_Estimated_Distance_KM"],
        ascending=[False, False],
        na_position="last",
    )

    distance_columns = [
        "Mean_Estimated_Distance_KM",
        "Median_Estimated_Distance_KM",
        "Maximum_Estimated_Distance_KM",
    ]
    routes[distance_columns] = routes[distance_columns].round(2)
    routes.to_csv(ROUTE_OUT, index=False)

    # Factory-level overview for comparison.
        # Count product lines from the original dataset.
    factory_line_summary = (
        df.groupby("Factory", dropna=False)
        .agg(
            Order_Lines=("Row ID", "count"),
        )
        .reset_index()
    )

    # Calculate order counts and distance statistics once per order.
    factory_order_summary = (
        order_df.groupby("Factory", dropna=False)
        .agg(
            Distinct_Orders=("Order ID", "nunique"),
            Mean_Estimated_Distance_KM=(
                "Straight_Line_Distance_KM", "mean"
            ),
            Missing_Distance_Rows=(
                "Straight_Line_Distance_KM",
                lambda values: int(values.isna().sum()),
            ),
        )
        .reset_index()
    )

    factory_summary = factory_line_summary.merge(
        factory_order_summary,
        on="Factory",
        how="left",
        validate="one_to_one",
    )

    # Count distinct factory-destination combinations.
    destination_counts = (
        order_df.groupby("Factory", dropna=False)[
            ["Country/Region", "State/Province", "City", "Postal Code"]
        ]
        .apply(lambda group: group.drop_duplicates().shape[0])
        .rename("Distinct_Destination_Groups")
        .reset_index()
    )

    factory_summary = factory_summary.merge(
        destination_counts,
        on="Factory",
        how="left",
        validate="one_to_one",
    )

    factory_summary["Mean_Estimated_Distance_KM"] = (
        factory_summary["Mean_Estimated_Distance_KM"].round(2)
    )

    factory_summary.to_csv(SUMMARY_OUT, index=False)

    print("Source rows:", len(df))
    print("Unique order lines:", df["Row ID"].nunique())
    print("Factory-destination groups:", len(routes))
    print("Factories:", df["Factory"].nunique())
    print(
        "Unique orders with missing distances:",
        int(order_df["Straight_Line_Distance_KM"].isna().sum()),
    )

    print("\nFactory summary:")
    print(factory_summary.to_string(index=False))

    print("\nTen highest-volume factory-destination groups:")
    print(
        routes[
            route_columns
            + [
                "Order_Lines",
                "Distinct_Orders",
                "Mean_Estimated_Distance_KM",
            ]
        ].head(10).to_string(index=False)
    )

    print("\nSaved reports:")
    print(ROUTE_OUT)
    print(SUMMARY_OUT)

    print(
        "\nLimitations: distances are straight-line estimates, not "
        "road distances. Coordinates may be uncertain. The date "
        "anomaly remains unresolved, so delivery-time performance "
        "has not been validated."
    )


if __name__ == "__main__":
    main()
