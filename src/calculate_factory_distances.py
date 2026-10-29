
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

ORDERS_PATH = ROOT / "data" / "processed" / "nassau_shipping_audited.csv"
GEO_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"

OUTPUT_PATH = ROOT / "data" / "processed" / "factory_destination_distances.csv"
SUMMARY_PATH = ROOT / "reports" / "factory_distance_summary.csv"

# Factory coordinates: latitude, longitude.
FACTORIES = {
    "Lot's O' Nuts": (32.881893, -111.768036),
    "Wicked Choccy's": (32.076176, -81.088371),
    "Sugar Shack": (48.119140, -96.181150),
    "Secret Factory": (41.446333, -90.565487),
    "The Other Factory": (35.117500, -89.971107),
}

# Product-to-factory mapping from the project's documented mapping.
PRODUCT_TO_FACTORY = {
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

# Geocoding statuses that should be explicitly flagged.
APPROXIMATE_STATUSES = {
    "Review",
    "Found_Canada_FSA",
    "Retry_Found",
}


def normalize_text(series):
    """Normalize join text without modifying the source columns."""
    return series.fillna("").astype(str).str.strip().str.casefold()


def normalize_postal(series):
    """
    Normalize postal codes for joining.
    Preserve Canadian postal codes and restore leading zeros in numeric US ZIPs.
    """
    def clean(value):
        if pd.isna(value):
            return ""
        value = str(value).strip()
        if value.endswith(".0"):
            value = value[:-2]

        # Restore leading zeros for numeric US ZIP codes.
        if value.isdigit() and len(value) <= 5:
            return value.zfill(5)

        # Canadian postal codes and other alphanumeric codes:
        # remove internal spaces and normalize case.
        return "".join(value.split()).upper()

    return series.apply(clean)


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between coordinates, in kilometres."""
    earth_radius_km = 6371.0088

    lat1, lon1, lat2, lon2 = map(
        np.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    # Guard against floating-point values slightly outside [0, 1].
    a = np.clip(a, 0, 1)

    return 2 * earth_radius_km * np.arcsin(np.sqrt(a))


def main():
    orders = pd.read_csv(ORDERS_PATH, dtype={"Postal Code": str})
    geo = pd.read_csv(GEO_PATH, dtype={"Postal Code": str})

    required_order_cols = [
        "Row ID", "Order ID", "Country/Region", "State/Province",
        "City", "Postal Code", "Product Name", "Units", "Sales",
    ]
    required_geo_cols = [
        "Country/Region", "State/Province", "City", "Postal Code",
        "Latitude", "Longitude", "Lookup_Status",
    ]

    for col in required_order_cols:
        if col not in orders.columns:
            raise ValueError(f"Missing order-data column: {col}")

    for col in required_geo_cols:
        if col not in geo.columns:
            raise ValueError(f"Missing geocoding column: {col}")

    # Create normalized keys in both dataframes.
    key_cols = ["Country/Region", "State/Province", "City"]

    for col in key_cols:
        orders[f"_key_{col}"] = normalize_text(orders[col])
        geo[f"_key_{col}"] = normalize_text(geo[col])

    orders["_key_Postal Code"] = normalize_postal(orders["Postal Code"])
    geo["_key_Postal Code"] = normalize_postal(geo["Postal Code"])

    join_keys = [
        "_key_Country/Region",
        "_key_State/Province",
        "_key_City",
        "_key_Postal Code",
    ]

    # Each geocoding key should identify at most one destination record.
    duplicates = geo.duplicated(join_keys, keep=False)
    if duplicates.any():
        print("WARNING: duplicate geocoding keys detected:")
        print(
            geo.loc[duplicates, required_geo_cols]
            .sort_values(["Country/Region", "State/Province", "City"])
            .to_string(index=False)
        )
        raise ValueError(
            "Geocoding keys are not unique. Resolve duplicate keys before joining."
        )

    geo["Latitude"] = pd.to_numeric(geo["Latitude"], errors="coerce")
    geo["Longitude"] = pd.to_numeric(geo["Longitude"], errors="coerce")

    # Keep the geocoding columns needed in the final dataset.
    geo_for_join = geo[
        join_keys
        + ["Latitude", "Longitude", "Lookup_Status", "Match_Display_Name", "Match_Count"]
    ].copy()

    merged = orders.merge(
        geo_for_join,
        on=join_keys,
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    merged["Factory"] = merged["Product Name"].map(PRODUCT_TO_FACTORY)
    merged["Factory_Latitude"] = merged["Factory"].map(
        {name: coords[0] for name, coords in FACTORIES.items()}
    )
    merged["Factory_Longitude"] = merged["Factory"].map(
        {name: coords[1] for name, coords in FACTORIES.items()}
    )

    merged["Geocoding_Matched"] = merged["_merge"].eq("both")
    merged["Factory_Mapped"] = merged["Factory"].notna()

    merged["Coordinate_Confidence_Flag"] = np.select(
        [
            ~merged["Geocoding_Matched"],
            merged["Lookup_Status"].isin(APPROXIMATE_STATUSES),
            merged["Lookup_Status"].eq("Found"),
        ],
        [
            "No geocoding match",
            "Approximate or requires review",
            "Found, not independently verified",
        ],
        default="Unclassified status",
    )

    valid = (
        merged["Geocoding_Matched"]
        & merged["Factory_Mapped"]
        & merged["Latitude"].between(-90, 90)
        & merged["Longitude"].between(-180, 180)
    )

    merged["Straight_Line_Distance_KM"] = np.nan

    merged.loc[valid, "Straight_Line_Distance_KM"] = haversine_km(
        merged.loc[valid, "Factory_Latitude"].to_numpy(),
        merged.loc[valid, "Factory_Longitude"].to_numpy(),
        merged.loc[valid, "Latitude"].to_numpy(),
        merged.loc[valid, "Longitude"].to_numpy(),
    )

    # Keep original data columns and add analysis fields.
    output_cols = [
        "Row ID", "Order ID", "Order Date", "Ship Date",
        "Country/Region", "State/Province", "City", "Postal Code",
        "Product ID", "Product Name", "Units", "Sales",
        "Factory", "Factory_Latitude", "Factory_Longitude",
        "Latitude", "Longitude", "Lookup_Status",
        "Match_Display_Name", "Match_Count",
        "Geocoding_Matched", "Factory_Mapped",
        "Coordinate_Confidence_Flag", "Straight_Line_Distance_KM",
    ]

    for col in output_cols:
        if col not in merged.columns:
            merged[col] = np.nan

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    merged[output_cols].to_csv(OUTPUT_PATH, index=False)

    # Summary is descriptive only; distances are not road-route distances.
    summary = (
        merged.groupby("Factory", dropna=False)
        .agg(
            Order_Lines=("Row ID", "count"),
            Distinct_Orders=("Order ID", "nunique"),
            Matched_Destination_Lines=("Geocoding_Matched", "sum"),
            Mapped_Product_Lines=("Factory_Mapped", "sum"),
            Mean_Straight_Line_KM=("Straight_Line_Distance_KM", "mean"),
            Median_Straight_Line_KM=("Straight_Line_Distance_KM", "median"),
            Max_Straight_Line_KM=("Straight_Line_Distance_KM", "max"),
        )
        .reset_index()
    )

    summary.to_csv(SUMMARY_PATH, index=False)

    print("Input order lines:", len(orders))
    print("Output distance rows:", len(merged))
    print("Rows matched to geocoding:", int(merged["Geocoding_Matched"].sum()))
    print("Rows with a mapped factory:", int(merged["Factory_Mapped"].sum()))
    print(
        "Rows with calculated distances:",
        int(merged["Straight_Line_Distance_KM"].notna().sum()),
    )
    print(
        "Rows with missing geocoding match:",
        int((~merged["Geocoding_Matched"]).sum()),
    )
    print(
        "Rows with unmapped products:",
        int((~merged["Factory_Mapped"]).sum()),
    )

    print("\nFactory distance summary:")
    print(summary.to_string(index=False))

    print(f"\nSaved detailed dataset: {OUTPUT_PATH}")
    print(f"Saved factory summary: {SUMMARY_PATH}")
    print(
        "\nCaution: distances are Haversine straight-line estimates, "
        "not road distances or delivery transit times."
    )


if __name__ == "__main__":
    main()
