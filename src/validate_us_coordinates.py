
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"

SHAPEFILE_PATH = (
    ROOT
    / "data"
    / "reference"
    / "us_zcta_2025"
    / "tl_2025_us_zcta520.shp"
)

OUTPUT_PATH = ROOT / "reports" / "us_coordinate_validation.csv"


def normalize_zip(value):
    """Normalize a US ZIP code to five digits."""
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.endswith(".0"):
        value = value[:-2]

    digits = "".join(char for char in value if char.isdigit())

    if not digits:
        return None

    return digits.zfill(5) if len(digits) <= 5 else None


def main():
    print("Loading geocoded destinations...")

    destinations = pd.read_csv(INPUT_PATH, dtype=str)

    required_columns = [
        "Country/Region",
        "Postal Code",
        "Latitude",
        "Longitude",
    ]

    missing = [
        column for column in required_columns
        if column not in destinations.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    destinations["ZIP5"] = destinations["Postal Code"].apply(
        normalize_zip
    )

    destinations["Latitude"] = pd.to_numeric(
        destinations["Latitude"], errors="coerce"
    )

    destinations["Longitude"] = pd.to_numeric(
        destinations["Longitude"], errors="coerce"
    )

    us = destinations[
        destinations["Country/Region"].str.strip().str.lower()
        .isin(["united states", "us", "usa"])
    ].copy()

    us = us.dropna(
        subset=["ZIP5", "Latitude", "Longitude"]
    )

    print(f"US destinations to validate: {len(us)}")

    print("Loading Census ZCTA boundaries...")

    zctas = gpd.read_file(
        SHAPEFILE_PATH,
        engine="pyogrio",
        columns=["ZCTA5CE20"],
    )

    zctas = zctas.rename(
        columns={"ZCTA5CE20": "ZIP5"}
    )

    zctas["ZIP5"] = zctas["ZIP5"].astype(str).str.zfill(5)

    print(f"Census ZCTA boundaries loaded: {len(zctas)}")

    print("Matching destination ZIP codes...")

    merged = us.merge(
        zctas,
        on="ZIP5",
        how="left",
        indicator=True,
    )

    matched = merged[merged["_merge"] == "both"].copy()
    unmatched = merged[merged["_merge"] == "left_only"].copy()

    print(f"ZIP codes with a ZCTA match: {len(matched)}")
    print(f"ZIP codes without a ZCTA match: {len(unmatched)}")

    print("Checking coordinate containment...")

    points = gpd.GeoDataFrame(
        matched,
        geometry=gpd.points_from_xy(
            matched["Longitude"],
            matched["Latitude"],
        ),
        crs="EPSG:4326",
    )

    if zctas.crs != points.crs:
        points = points.to_crs(zctas.crs)

    points["Coordinate_In_Matching_ZCTA"] = points.geometry.apply(
        lambda point, polygons=zctas.set_index("ZIP5").geometry:
            point.within(polygons.loc[points.loc[point.name, "ZIP5"]])
            if False else False
    )

    # Use a spatial join for the actual point-in-polygon test.
    polygons = zctas[["ZIP5", "geometry"]].copy()

    if polygons.crs != points.crs:
        polygons = polygons.to_crs(points.crs)

    joined = gpd.sjoin(
        points,
        polygons,
        how="left",
        predicate="within",
        lsuffix="destination",
        rsuffix="boundary",
    )

    joined["Coordinate_In_Matching_ZCTA"] = (
        joined["ZIP5_destination"]
        == joined["ZIP5_boundary"]
    )

    joined["Validation_Status"] = joined[
        "Coordinate_In_Matching_ZCTA"
    ].map({
        True: "Inside matching ZCTA",
        False: "Outside matching ZCTA",
    })

    unmatched["Coordinate_In_Matching_ZCTA"] = pd.NA
    unmatched["Validation_Status"] = "No matching ZCTA boundary"

    results = pd.concat(
        [joined, unmatched],
        ignore_index=True,
    )

    results["Validation_Method"] = (
        "Point-in-polygon against 2025 Census ZCTA boundaries"
    )

    results["Accuracy_Limitation"] = (
        "ZCTA containment does not prove exact postal-address accuracy"
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results.drop(
        columns=["geometry"],
        errors="ignore",
    ).to_csv(OUTPUT_PATH, index=False)

    print("\nVALIDATION SUMMARY")
    print("------------------")

    print(
        results["Validation_Status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print(f"\nReport saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
