
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = ROOT / "data" / "raw" / "Nassau Candy Distributor.csv"
DISTANCE_FILE = (
    ROOT / "data" / "processed"
    / "factory_destination_distances.csv"
)

REPORTS = {
    "factory_destination_route_analysis.csv":
        ROOT / "reports" / "factory_destination_route_analysis.csv",
    "route_priority_analysis.csv":
        ROOT / "reports" / "route_priority_analysis.csv",
    "ship_mode_analysis.csv":
        ROOT / "reports" / "ship_mode_analysis.csv",
    "analysis_quality_summary.csv":
        ROOT / "reports" / "analysis_quality_summary.csv",
}

print("=" * 60)
print("FINAL PROJECT VALIDATION")
print("=" * 60)

errors = []

# 1. Check required files
required_files = [RAW_FILE, DISTANCE_FILE, *REPORTS.values()]

for file in required_files:
    if file.exists():
        print(f"[OK] File exists: {file.name}")
    else:
        print(f"[FAIL] Missing file: {file}")
        errors.append(f"Missing file: {file.name}")

if errors:
    print("\nFix missing files before continuing.")
    raise SystemExit(1)

# 2. Load source and processed data
raw = pd.read_csv(RAW_FILE)
distance = pd.read_csv(DISTANCE_FILE)

print("\n--- Source and processed data ---")
print("Raw rows:", len(raw))
print("Distance rows:", len(distance))

if len(raw) == len(distance):
    print("[OK] Row counts match")
else:
    errors.append("Raw and distance row counts differ")
    print("[FAIL] Row counts differ")

# 3. Validate the Row ID join key
for name, frame in [("Raw", raw), ("Distance", distance)]:
    if "Row ID" not in frame.columns:
        errors.append(f"{name} file has no Row ID column")
        print(f"[FAIL] {name}: Row ID column missing")
        continue

    missing = int(frame["Row ID"].isna().sum())
    duplicates = int(frame["Row ID"].duplicated().sum())

    print(f"{name} missing Row IDs:", missing)
    print(f"{name} duplicate Row IDs:", duplicates)

    if missing or duplicates:
        errors.append(f"{name} Row IDs are not unique and complete")

if "Row ID" in raw.columns and "Row ID" in distance.columns:
    raw_ids = set(raw["Row ID"].dropna())
    distance_ids = set(distance["Row ID"].dropna())

    print("Processed IDs absent from raw:", len(distance_ids - raw_ids))
    print("Raw IDs absent from processed:", len(raw_ids - distance_ids))

    if raw_ids != distance_ids:
        errors.append("Row ID sets differ")

# 4. Validate distance values
print("\n--- Distance checks ---")

if "Straight_Line_Distance_KM" not in distance.columns:
    errors.append("Distance column missing")
else:
    distances = pd.to_numeric(
        distance["Straight_Line_Distance_KM"],
        errors="coerce",
    )

    missing_distances = int(distances.isna().sum())
    negative_distances = int((distances < 0).sum())

    print("Missing distances:", missing_distances)
    print("Negative distances:", negative_distances)

    if missing_distances or negative_distances:
        errors.append("Distance values contain missing or negative values")

# 5. Validate report totals
print("\n--- Report checks ---")

for name, path in REPORTS.items():
    report = pd.read_csv(path)
    print(f"{name}: {len(report)} rows")

route_path = REPORTS["factory_destination_route_analysis.csv"]
route = pd.read_csv(route_path)

if "Order_Lines" in route.columns:
    route_total = int(route["Order_Lines"].sum())
    print("Route report order lines:", route_total)

    if route_total != len(raw):
        errors.append("Route report total does not match raw row count")
    else:
        print("[OK] Route report totals match")

ship_path = REPORTS["ship_mode_analysis.csv"]
ship = pd.read_csv(ship_path)

if "Order_Lines" in ship.columns:
    ship_total = int(ship["Order_Lines"].sum())
    print("Ship-mode report order lines:", ship_total)

    if ship_total != len(raw):
        errors.append("Ship-mode report total does not match raw row count")
    else:
        print("[OK] Ship-mode report totals match")

# 6. Verify date anomaly without changing the source dates
print("\n--- Date anomaly check ---")

if {"Order Date", "Ship Date"}.issubset(raw.columns):
    order_dates = pd.to_datetime(
        raw["Order Date"], dayfirst=True, errors="coerce"
    )
    ship_dates = pd.to_datetime(
        raw["Ship Date"], dayfirst=True, errors="coerce"
    )

    valid = order_dates.notna() & ship_dates.notna()
    intervals = (ship_dates[valid] - order_dates[valid]).dt.days

    print("Unparseable order dates:", int(order_dates.isna().sum()))
    print("Unparseable ship dates:", int(ship_dates.isna().sum()))
    print("Valid date intervals:", len(intervals))

    if len(intervals):
        print("Intervals over 365 days:", int((intervals > 365).sum()))
        print("Minimum interval (days):", int(intervals.min()))
        print("Median interval (days):", float(intervals.median()))
        print("Maximum interval (days):", int(intervals.max()))

        print(
            "NOTE: Preserve the original dates. "
            "Do not treat these intervals as validated delivery times."
        )
else:
    errors.append("Required date columns are missing")

# 7. Final result
print("\n" + "=" * 60)

if errors:
    print("VALIDATION NEEDS ATTENTION")
    for error in errors:
        print("-", error)
else:
    print("STRUCTURAL VALIDATION PASSED")
    print("Review the output above before finalizing the report.")

print("=" * 60)
