
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent

DISTANCE_FILE = (
    ROOT / "data" / "processed"
    / "geographically_audited_distances.csv"
)

QUALITY_FILE = (
    ROOT / "reports"
    / "analysis_quality_summary.csv"
)

RAW_FILE = (
    ROOT / "data" / "raw"
    / "Nassau Candy Distributor.csv"
)

st.set_page_config(
    page_title="Nassau Candy | Shipping Analysis",
    page_icon="📦",
    layout="wide",
)

# Compact dashboard styling

st.markdown(
    """
    <style>
    /* Main page spacing */
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 1.5rem;
        padding-left: 1.8rem;
        padding-right: 1.8rem;
        max-width: 1600px;
    }

    /* Consistent typography */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h2 {
        font-size: 1.3rem !important;
        font-weight: 650 !important;
    }

    h3 {
        font-size: 1.02rem !important;
        font-weight: 600 !important;
    }

    p, li {
        font-size: 0.88rem;
        line-height: 1.55;
    }

    /* KPI cards */
    [data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.07);
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 10px;
        padding: 14px 16px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 650 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.18);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 1.1rem !important;
    }

    [data-testid="stSidebar"] label {
        font-size: 0.84rem !important;
        font-weight: 500;
    }

    /* Tabs */
    div[data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.22);
    }

    div[data-baseweb="tab-list"] button {
        font-size: 0.86rem;
        padding: 10px 14px;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Alerts and explanations */
    [data-testid="stAlert"] {
        border-radius: 8px;
    }

    /* Dividers */
    hr {
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
        border-color: rgba(128, 128, 128, 0.22);
    }

    /* Small screens */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 2. Dashboard heading
# --------------------------------------------------

st.title("Nassau Candy Distributor")

st.subheader(
    "Factory-to-Customer Shipping Distance Analysis"
)

st.caption(
    "Research dashboard | Geographic distance estimates | "
    "Straight-line distance, not road distance"
)

st.info(
    "Data limitation: destination coordinates have not been "
    "independently verified. The order/ship-date anomaly remains "
    "unresolved. This analysis does not calculate actual truck "
    "routes, delivery times, or shipping costs."
)

# --------------------------------------------------
# 3. Load processed distance data
# --------------------------------------------------

if not DISTANCE_FILE.exists():
    st.error(
        f"Distance data file not found: {DISTANCE_FILE}"
    )
    st.stop()

df = pd.read_csv(DISTANCE_FILE)

# Join order-level attributes from the original source dataset.
if not RAW_FILE.exists():
    st.error(
        f"Original source data file not found: {RAW_FILE}. "
        "It is required for Region, Ship Mode, and Order Date filters."
    )
    st.stop()

source_orders = pd.read_csv(RAW_FILE)
order_attribute_columns = [
    "Order ID", "Region", "Ship Mode", "Order Date", "Ship Date"
]
missing_order_attributes = [
    column for column in order_attribute_columns
    if column not in source_orders.columns
]
if missing_order_attributes:
    st.error(
        "Original source data is missing required order attributes: "
        f"{missing_order_attributes}"
    )
    st.stop()

order_attributes = source_orders[order_attribute_columns].copy()
attribute_consistency = (
    order_attributes.groupby("Order ID")[[
        "Region", "Ship Mode", "Order Date", "Ship Date"
    ]].nunique(dropna=False)
)
if (attribute_consistency > 1).any().any():
    st.error(
        "Some Order IDs have conflicting Region, Ship Mode, or date "
        "values. Filters were stopped to avoid incorrect joins."
    )
    st.stop()

order_attributes = order_attributes.drop_duplicates(
    subset=["Order ID"]
)

# Remove existing copies of these attributes to prevent
# pandas from creating _x and _y column names.
columns_to_refresh = [
    "Region",
    "Ship Mode",
    "Order Date",
    "Ship Date",
]

df = df.drop(
    columns=[
        column
        for column in columns_to_refresh
        if column in df.columns
    ]
)

# Join the authoritative order attributes from the source data.
df = df.merge(
    order_attributes,
    on="Order ID",
    how="left",
    validate="many_to_one",
)
df["Order_Date_Parsed"] = pd.to_datetime(
    df["Order Date"], dayfirst=True, errors="coerce"
)

required_columns = [
    "Row ID",
    "Order ID",
    "Factory",
    "City",
    "State/Province",
    "Country/Region",
    "Lookup_Status",
    "Straight_Line_Distance_KM",
    "Geographic_Validation_Result",
    "Geographic_Validation_Usable",
    "Distance_Interpretation",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"Missing required columns: {missing_columns}"
    )
    st.stop()

df["Straight_Line_Distance_KM"] = pd.to_numeric(
    df["Straight_Line_Distance_KM"],
    errors="coerce",
)

df["Geographic_Validation_Usable"] = (
    df["Geographic_Validation_Usable"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({
        "true": True,
        "false": False,
    })
)

# Support files that do not contain postal codes
if "Postal Code" not in df.columns:
    df["Postal Code"] = ""

# --------------------------------------------------
# 4. Sidebar filters
# --------------------------------------------------

st.sidebar.header("Filters")

factory_options = sorted(
    df["Factory"].dropna().astype(str).unique().tolist()
)

status_options = sorted(
    df["Lookup_Status"].dropna().astype(str).unique().tolist()
)

country_options = sorted(
    df["Country/Region"].dropna().astype(str).unique().tolist()
)

region_options = sorted(
    df["Region"].dropna().astype(str).unique().tolist()
)
ship_mode_options = sorted(
    df["Ship Mode"].dropna().astype(str).unique().tolist()
)

valid_order_dates = df["Order_Date_Parsed"].dropna()
if valid_order_dates.empty:
    st.error("No valid Order Date values are available for exploration.")
    st.stop()

date_min = valid_order_dates.min().date()
date_max = valid_order_dates.max().date()
st.sidebar.caption(
    "Order Date is an exploration filter only. Recorded order-to-ship "
    "intervals are anomalous and are not delivery-performance measures. "
    "A lead-time threshold control is intentionally omitted."
)
selected_order_dates = st.sidebar.date_input(
    "Order Date range (exploration only)",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)
if not isinstance(selected_order_dates, tuple):
    selected_order_dates = (
        selected_order_dates,
        selected_order_dates,
    )
elif len(selected_order_dates) == 1:
    selected_order_dates = (
        selected_order_dates[0],
        selected_order_dates[0],
    )

selected_factories = st.sidebar.multiselect(
    "Factory",
    factory_options,
    default=factory_options,
)

selected_statuses = st.sidebar.multiselect(
    "Geocoding status",
    status_options,
    default=status_options,
)

selected_countries = st.sidebar.multiselect(
    "Country",
    country_options,
    default=country_options,
)

selected_regions = st.sidebar.multiselect(
    "Region",
    region_options,
    default=region_options,
)
selected_ship_modes = st.sidebar.multiselect(
    "Ship Mode",
    ship_mode_options,
    default=ship_mode_options,
)

geographic_options = sorted(
    df["Geographic_Validation_Result"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_geographic_statuses = st.sidebar.multiselect(
    "Geographic validation",
    geographic_options,
    default=geographic_options,
    help=(
        "Inside matching reference areas, outside matching areas, "
        "or without a matching reference boundary."
    ),
)

# Apply all selected filters

filtered = df[
    df["Factory"].astype(str).isin(selected_factories)
    & df["Lookup_Status"].astype(str).isin(
        selected_statuses
    )
    & df["Country/Region"].astype(str).isin(
        selected_countries
    )
    & df["Region"].astype(str).isin(selected_regions)
    & df["Ship Mode"].astype(str).isin(selected_ship_modes)
    & df["Order_Date_Parsed"].dt.date.between(
        selected_order_dates[0], selected_order_dates[1]
    )
    & df["Geographic_Validation_Result"].astype(str).isin(
        selected_geographic_statuses
    )
].copy()

if filtered.empty:
    st.warning(
        "No records match these filters. "
        "Change your selections in the sidebar."
    )
    st.stop()

# --------------------------------------------------
# 5. KPI metrics
# --------------------------------------------------
# One record per order to prevent multi-product
# orders from receiving extra weight.
order_level_filtered = filtered.drop_duplicates(
    subset=["Order ID"]
)

verified_orders = order_level_filtered[
    order_level_filtered["Geographic_Validation_Usable"].eq(True)
].copy()

overall_mean = verified_orders[
    "Straight_Line_Distance_KM"
].mean()

destination_count = filtered[
    ["Country/Region", "State/Province", "City"]
].drop_duplicates().shape[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Order lines",
    f"{len(filtered):,}",
)

col2.metric(
    "Distinct orders",
    f"{filtered['Order ID'].nunique():,}",
)

col3.metric(
    "Mean distance (verified orders)",
    (
        f"{overall_mean:,.2f} km"
        if pd.notna(overall_mean)
        else "N/A"
    ),
)

col4.metric(
    "Destinations",
    f"{destination_count:,}",
)

st.divider()


# --------------------------------------------------
# Ship-mode comparison
# --------------------------------------------------

st.divider()
st.subheader("Shipping Method Comparison")

st.caption(
    "Compare order-line volume and estimated straight-line distance "
    "by shipping method. These results do not measure delivery speed, "
    "shipping cost, or overall shipping efficiency."
)

ship_mode_file = ROOT / "reports" / "ship_mode_analysis.csv"

ship_mode_colors = {
    "First Class": "#8B5CF6",
    "Same Day": "#F59E0B",
    "Second Class": "#14B8A6",
    "Standard Class": "#3B82F6",
}


if ship_mode_file.exists():
    ship_mode_data = pd.read_csv(ship_mode_file)

    numeric_columns = [
        "Unique_Orders",
        "Order_Share_Percent",
        "Average_Order_Value",
        "Gross_Margin_Percent",
    ]

    for column in numeric_columns:
        ship_mode_data[column] = pd.to_numeric(
            ship_mode_data[column],
            errors="coerce",
        )

    ship_mode_data = ship_mode_data.rename(
        columns={"Ship_Mode": "Ship Mode"}
    )

    left_ship, right_ship = st.columns(2)

    with left_ship:
        st.markdown("#### Orders by shipping method")

        volume_data = ship_mode_data.dropna(
            subset=["Ship Mode", "Unique_Orders"]
        ).sort_values("Unique_Orders", ascending=False)

        fig_ship_volume = px.bar(
            volume_data,
            x="Ship Mode",
            y="Unique_Orders",
            text="Unique_Orders",
            color="Ship Mode",
            color_discrete_map=ship_mode_colors,
            labels={
                "Unique_Orders": "Unique orders",
                "Ship Mode": "Shipping method",
            },
        )

        fig_ship_volume.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )

        fig_ship_volume.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Shipping method",
            yaxis_title="Unique orders",
            xaxis_tickangle=-15,
            margin=dict(l=20, r=25, t=35, b=65),
        )

        st.plotly_chart(
            fig_ship_volume,
            width="stretch",
        )

    with right_ship:
        st.markdown("#### Average order value by shipping method")

        value_data = ship_mode_data.dropna(
            subset=["Ship Mode", "Average_Order_Value"]
        ).sort_values("Average_Order_Value", ascending=False)

        fig_ship_value = px.bar(
            value_data,
            x="Ship Mode",
            y="Average_Order_Value",
            text="Average_Order_Value",
            color="Ship Mode",
            color_discrete_map=ship_mode_colors,
            labels={
                "Average_Order_Value": "Average order value ($)",
                "Ship Mode": "Shipping method",
            },
        )

        fig_ship_value.update_traces(
            texttemplate="$%{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
        )

        fig_ship_value.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Shipping method",
            yaxis_title="Average order value ($)",
            xaxis_tickangle=-15,
            margin=dict(l=20, r=25, t=35, b=65),
        )

        st.plotly_chart(
            fig_ship_value,
            width="stretch",
        )

    st.caption(
        "This report summarizes all 8,549 orders and is independent "
        "of the dashboard sidebar filters. It describes order volume "
        "and sales value, not delivery speed or shipping cost."
    )

    st.markdown("#### Shipping method summary")

    st.dataframe(
        ship_mode_data,
        width="stretch",
        hide_index=True,
    )

else:
    st.warning(
        "Ship-mode report not found. Run "
        "src/build_ship_mode_analysis.py first."
    )



# --------------------------------------------------
# 6. Create dashboard tabs
# --------------------------------------------------

factory_tab, destination_tab, quality_tab, methodology_tab = (
    st.tabs(
        [
            "Factory comparison",
            "Destination analysis",
            "Data quality",
            "Methodology",
        ]
    )
)


# --------------------------------------------------
# 7. Factory comparison tab
# --------------------------------------------------

with factory_tab:
    st.subheader("Factory performance overview")

    st.caption(
        "Compare order-line volume and average geographic "
        "distance for the selected factories."
    )

    factory_summary = (
    verified_orders.groupby("Factory", dropna=False)
    .agg(
        Unique_Orders=("Order ID", "nunique"),
        Mean_Distance_KM=(
            "Straight_Line_Distance_KM",
            "mean",
        ),
        Median_Distance_KM=(
            "Straight_Line_Distance_KM",
            "median",
        ),
        Minimum_Distance_KM=(
            "Straight_Line_Distance_KM",
            "min",
        ),
        Maximum_Distance_KM=(
            "Straight_Line_Distance_KM",
            "max",
        ),
    )
    .reset_index()
)

    factory_summary["Mean_Distance_KM"] = (
        factory_summary["Mean_Distance_KM"].round(2)
    )
    factory_summary["Median_Distance_KM"] = (
        factory_summary["Median_Distance_KM"].round(2)
    )
    factory_summary["Minimum_Distance_KM"] = (
        factory_summary["Minimum_Distance_KM"].round(2)
    )
    factory_summary["Maximum_Distance_KM"] = (
        factory_summary["Maximum_Distance_KM"].round(2)
    )


    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.markdown("#### Average distance by factory")

        distance_chart_data = factory_summary.dropna(
            subset=["Factory", "Mean_Distance_KM"]
        ).sort_values("Mean_Distance_KM", ascending=False)

        fig_distance = px.bar(
            distance_chart_data,
            x="Factory",
            y="Mean_Distance_KM",
            color="Factory",
            text="Mean_Distance_KM",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={
                "Factory": "Factory",
                "Mean_Distance_KM": "Mean distance (km)",
            },
        )

        fig_distance.update_traces(
            texttemplate="%{text:,.0f} km",
            textposition="outside",
            cliponaxis=False,
        )

        fig_distance.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=15, r=20, t=30, b=75),
            xaxis_title="Factory",
            yaxis_title="Mean straight-line distance (km)",
            xaxis_tickangle=-20,
        )

        st.plotly_chart(fig_distance, width="stretch")

        st.caption(
            "Higher values indicate greater average geographic "
            "separation between factory and destination coordinates. "
            "They do not establish actual delivery distance."
        )

    with right_chart:
        st.markdown("#### Verified orders by factory")

        volume_chart_data = factory_summary.dropna(
            subset=["Factory", "Unique_Orders"]
        ).sort_values("Unique_Orders", ascending=False)

        fig_volume = px.bar(
            volume_chart_data,
            x="Factory",
            y="Unique_Orders",
            color="Factory",
            text="Unique_Orders",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            labels={
                "Factory": "Factory",
                "Unique_Orders": "Verified unique orders",
            },
        )

        fig_volume.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )

        fig_volume.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=15, r=20, t=30, b=75),
            xaxis_title="Factory",
            yaxis_title="Verified unique orders",
            xaxis_tickangle=-20,
        )

        st.plotly_chart(fig_volume, width="stretch")

        st.caption(
    "Counts represent geographically verified unique orders "
    "assigned to each factory, not individual product lines."
)



    st.divider()

    st.markdown("#### Factory summary")

    display_factory_summary = factory_summary.rename(
        columns={
            "Factory": "Factory",
            "Unique_Orders": "Verified unique orders",
            "Mean_Distance_KM": "Mean distance (km)",
            "Median_Distance_KM": "Median distance (km)",
            "Minimum_Distance_KM": "Minimum distance (km)",
            "Maximum_Distance_KM": "Maximum distance (km)",
        }
    )
    st.dataframe(
        display_factory_summary,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Each order maps to exactly one factory in the audited data. "
        "Factory order counts therefore represent separate groups. "
        "These counts cover geographically verified orders only."
    )

    st.divider()

    st.markdown("#### Distance distribution by factory")

    box_data = verified_orders.dropna(
    subset=["Straight_Line_Distance_KM", "Factory"]
).copy()

    if not box_data.empty:
        fig_box = px.box(
            box_data,
            x="Factory",
            y="Straight_Line_Distance_KM",
            color="Factory",
            points="outliers",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={
                "Factory": "Factory",
                "Straight_Line_Distance_KM": (
                    "Straight-line distance (km)"
                ),
            },
        )

        fig_box.update_layout(
             template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=360,
    margin=dict(l=10, r=15, t=15, b=65),
    xaxis_title="",
    yaxis_title="Straight-line distance (km)",
    xaxis_tickangle=-15,
    font=dict(size=12),
    yaxis=dict(
        gridcolor="rgba(160,160,160,0.20)",
        zerolinecolor="rgba(160,160,160,0.25)",
    ),
    showlegend=False,
)


        st.plotly_chart(
            fig_box,
            width="stretch",
        )

        st.caption(
            "The box shows the median and interquartile range. "
            "Points beyond the whiskers are potential statistical "
            "outliers, not necessarily data errors."
        )
    else:
        st.warning(
            "No valid distance values are available for the box plot."
        )


# --------------------------------------------------
# Factory-to-destination analysis
# --------------------------------------------------

st.divider()
st.subheader("Factory-to-destination analysis")

st.caption(
    "Explore order volume and estimated straight-line distance "
    "between factories and customer destinations. These are not "
    "verified road distances or delivery times."
)

route_file = (
    ROOT
    / "reports"
    / "factory_destination_route_analysis.csv"
)

if not route_file.exists():
    st.warning(
        "Route analysis file not found. Run "
        "src/build_factory_destination_analysis.py first."
    )
else:
    route_data = pd.read_csv(route_file)

    # Destination filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        route_factories = sorted(
            route_data["Factory"].dropna().unique().tolist()
        )
        selected_factories = st.multiselect(
            "Factory",
            options=route_factories,
            default=route_factories,
            key="route_factory_filter",
        )

    with filter_col2:
        route_states = sorted(
            route_data["State/Province"].dropna().astype(str).unique()
        )
        selected_states = st.multiselect(
            "State / province",
            options=route_states,
            key="route_state_filter",
        )

    with filter_col3:
        route_countries = sorted(
            route_data["Country/Region"].dropna().astype(str).unique()
        )
        selected_countries = st.multiselect(
            "Country",
            options=route_countries,
            default=route_countries,
            key="route_country_filter",
        )

    route_filtered = route_data[
        route_data["Factory"].isin(selected_factories)
        & route_data["Country/Region"].astype(str).isin(
            selected_countries
        )
    ].copy()

    if selected_states:
        route_filtered = route_filtered[
            route_filtered["State/Province"].astype(str).isin(
                selected_states
            )
        ]

    if route_filtered.empty:
        st.info("No destination groups match these filters.")
    else:
        # Summary metrics
        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Factory-destination groups",
            f"{len(route_filtered):,}",
        )
        metric2.metric(
            "Order lines",
            f"{route_filtered['Order_Lines'].sum():,}",
        )
        metric3.metric(
            "Unique orders",
            f"{route_filtered['Distinct_Orders'].sum():,}",
        )

        st.caption(
        "Each order maps to one factory-destination group in the "
        "audited data. Therefore, distinct orders can be summed "
        "across these groups without double-counting."
        )


        left_route, right_route = st.columns(2)

        # Consistent factory colors for Highest-volume destinations only
        factory_colors = {
            "Lot's O' Nuts": "#D65DB1",
            "Wicked Choccy's": "#56B4E9",
            "Sugar Shack": "#F5A623",
            "Secret Factory": "#9561C7",
            "The Other Factory": "#36A878",
        }

        with left_route:
            st.markdown("#### Highest-volume destinations")

            volume_data = route_filtered.copy()

            volume_data["Distinct_Orders"] = pd.to_numeric(
                volume_data["Distinct_Orders"],
                errors="coerce",
            )

            volume_data = volume_data.dropna(
                subset=["Distinct_Orders", "City", "Factory"]
            ).nlargest(15, "Distinct_Orders").copy()

            if not volume_data.empty:
                volume_data["Destination"] = (
                    volume_data["City"].astype(str)
                    + ", "
                    + volume_data["State/Province"].fillna("").astype(str)
                )

                volume_data = volume_data.sort_values(
                    "Distinct_Orders",
                    ascending=False,
                )

                fig_route_volume = px.bar(
                    volume_data,
                    x="Destination",
                    y="Distinct_Orders",
                    color="Factory",
                    color_discrete_map=factory_colors,
                    text="Distinct_Orders",
                    hover_data=[
                    "Postal Code",
                    "Order_Lines",
                    "Distinct_Orders",
                    "Mean_Estimated_Distance_KM",
                    ],
                    labels={
                        "Distinct_Orders": "Unique orders",
                        "Destination": "Destination",
                        "Factory": "Factory",
                        "State/Province": "State / province",
                        "Postal Code": "Postal code",
                        "Order_Lines": "Product lines",
                        "Mean_Estimated_Distance_KM":
                            "Mean estimated distance (km)",
                    },
                )

                fig_route_volume.update_traces(
                    texttemplate="%{text:,.0f}",
                    textposition="outside",
                    cliponaxis=False,
                )

                fig_route_volume.update_layout(
                    height=560,
                    xaxis_title="Destination city",
                    yaxis_title="Unique orders",
                    xaxis_tickangle=-45,
                    legend_title="Factory",
                    margin=dict(l=15, r=25, t=30, b=140),
                )

                st.plotly_chart(
                    fig_route_volume,
                    width="stretch",
                )
            else:
                st.warning(
                    "No valid destination volume records are available "
                    "for the current filters."
                )

        with right_route:
            st.markdown("#### Longest estimated distances")

            distance_data = route_filtered.copy()

            distance_data["Mean_Estimated_Distance_KM"] = pd.to_numeric(
                distance_data["Mean_Estimated_Distance_KM"],
                errors="coerce",
            )

            distance_data = distance_data.dropna(
                subset=[
                    "Mean_Estimated_Distance_KM",
                    "City",
                    "Factory",
                ]
            ).nlargest(15, "Mean_Estimated_Distance_KM").copy()

            if not distance_data.empty:
                distance_data["Destination"] = (
                    distance_data["City"].astype(str)
                    + ", "
                    + distance_data["State/Province"].fillna("").astype(str)
                )

                fig_route_distance = px.bar(
                    distance_data.sort_values(
                        "Mean_Estimated_Distance_KM",
                        ascending=False,
                    ),
                    x="Destination",
                    y="Mean_Estimated_Distance_KM",
                    color="Factory",
                    text="Mean_Estimated_Distance_KM",
                    hover_data=[
                        "Country/Region",
                        "Postal Code",
                        "Order_Lines",
                        "Distinct_Orders",
                    ],
                    labels={
                        "Mean_Estimated_Distance_KM":
                            "Mean estimated distance (km)",
                        "Destination": "Destination",
                        "Factory": "Factory",
                        "Order_Lines": "Order lines",
                        "Distinct_Orders": "Distinct orders",
                    },
                )

                fig_route_distance.update_traces(
                    texttemplate="%{text:,.0f} km",
                    textposition="outside",
                    cliponaxis=False,
                )

                fig_route_distance.update_layout(
                    height=560,
                    xaxis_title="Destination",
                    yaxis_title="Mean estimated distance (km)",
                    xaxis_tickangle=-45,
                    legend_title="Factory",
                    margin=dict(l=15, r=25, t=30, b=140),
                )

                st.plotly_chart(
                    fig_route_distance,
                    width="stretch",
                )
            else:
                st.warning(
                    "No valid estimated-distance records are available "
                    "for the current filters."
                )



# --------------------------------------------------
# Route Investigation Priorities
# --------------------------------------------------

st.markdown("---")
st.subheader("Route Investigation Priorities")

priority_file = (
    Path(__file__).parent
    / "reports"
    / "route_priority_analysis.csv"
)

if priority_file.exists():
    priority_df = pd.read_csv(priority_file)

    priority_df["Mean_Estimated_Distance_KM"] = pd.to_numeric(
        priority_df["Mean_Estimated_Distance_KM"],
        errors="coerce",
    )

    priority_df["Order_Lines"] = pd.to_numeric(
        priority_df["Order_Lines"],
        errors="coerce",
    )
    priority_df["Distinct_Orders"] = pd.to_numeric(
    priority_df["Distinct_Orders"],
    errors="coerce",
    )

    priority_df["Investigation_Rank"] = pd.to_numeric(
        priority_df["Investigation_Rank"],
        errors="coerce",
    )

    st.caption(
        "Screening results to guide further investigation. "
        "These are not measured shipping-efficiency scores. "
        "Distances are straight-line estimates, and ambiguous "
        "geocoding results do not necessarily mean coordinates are wrong."
    )

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        available_factories = sorted(
            priority_df["Factory"].dropna().unique().tolist()
        )
        selected_factories = st.multiselect(
            "Filter factories",
            options=available_factories,
            default=available_factories,
            key="priority_factory_filter",
        )

    with filter_col2:
        available_categories = sorted(
            priority_df["Investigation_Category"]
            .dropna()
            .unique()
            .tolist()
        )
        selected_categories = st.multiselect(
            "Filter investigation categories",
            options=available_categories,
            default=available_categories,
            key="priority_category_filter",
        )

    filtered_priority = priority_df[
        priority_df["Factory"].isin(selected_factories)
        & priority_df["Investigation_Category"].isin(
            selected_categories
        )
    ].copy()

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Groups shown",
            f"{len(filtered_priority):,}",
        )

    with metric2:
        st.metric(
            "Unique orders represented",
            f"{int(filtered_priority['Distinct_Orders'].sum()):,}",
        )

    with metric3:
        valid_distance_groups = filtered_priority.dropna(
            subset=[
                "Mean_Estimated_Distance_KM",
                "Distinct_Orders",
            ]
        )

        total_orders = valid_distance_groups["Distinct_Orders"].sum()

        if filtered_priority.empty or total_orders == 0:
            st.metric("Mean estimated distance", "N/A")
        else:
            weighted_mean_distance = (
                valid_distance_groups["Mean_Estimated_Distance_KM"]
                * valid_distance_groups["Distinct_Orders"]
            ).sum() / total_orders

            st.metric(
                "Mean estimated distance",
                f"{weighted_mean_distance:,.1f} km",
            )

    if filtered_priority.empty:
        st.info("No route groups match the selected filters.")
    else:
        st.markdown("**Highest-ranked groups in the current selection**")

        display_columns = [
            "Investigation_Rank",
            "Factory",
            "Country/Region",
            "State/Province",
            "City",
            "Postal Code",
            "Order_Lines",
            "Distinct_Orders",
            "Mean_Estimated_Distance_KM",
            "Coordinate_Status_Flag_Rate_Pct",
            "Investigation_Category",
        ]

        display_columns = [
            col for col in display_columns
            if col in filtered_priority.columns
        ]

        st.dataframe(
            filtered_priority
            .sort_values("Investigation_Rank")
            [display_columns],
            width="stretch",
            hide_index=True,
        )

        st.download_button(
            "Download filtered priority report",
            data=filtered_priority[display_columns].to_csv(
                index=False
            ).encode("utf-8"),
            file_name="filtered_route_priority_analysis.csv",
            mime="text/csv",
            key="download_priority_report",
        )
else:
    st.warning(
        "Priority report not found. Run "
        "src/build_route_priority_analysis.py first."
    )


# --------------------------------------------------
# Factory and destination map
# --------------------------------------------------

st.markdown("---")
st.subheader("Factory and Customer Destination Map")

st.caption(
    "Factory and customer coordinates are shown geographically. "
    "Markers represent locations, not actual road routes. "
    "Some Canadian coordinates represent postal areas, and some "
    "destination matches require review."
)

distance_file = DISTANCE_FILE

if distance_file.exists():
    map_data = pd.read_csv(distance_file)

    map_data = map_data.dropna(
        subset=[
            "Latitude",
            "Longitude",
            "Factory_Latitude",
            "Factory_Longitude",
        ]
    ).copy()

    if map_data.empty:
        st.warning("No complete coordinates are available to map.")
    else:
        status_colors = {
            "Found": "#2E8B57",
            "Found_Canada_FSA": "#E3A008",
            "Retry_Found": "#6C63FF",
            "Review": "#D9485F",
        }

        map_data["Marker_Status"] = (
            map_data["Lookup_Status"].fillna("Unknown")
        )

        map_data["Coordinate_Type"] = map_data[
            "Marker_Status"
        ].map(
            {
                "Found": "Geocoded destination",
                "Found_Canada_FSA": "Approximate Canadian postal area",
                "Retry_Found": "Found after retry",
                "Review": "Ambiguous match - review needed",
            }
        ).fillna("Unknown status")

        map_destinations = (
            map_data[
                [
                    "City",
                    "State/Province",
                    "Country/Region",
                    "Latitude",
                    "Longitude",
                    "Marker_Status",
                    "Coordinate_Type",
                ]
            ]
            .drop_duplicates(
                subset=[
                    "Latitude",
                    "Longitude",
                    "Marker_Status",
                ]
            )
            .copy()
        )

        map_destinations["Location"] = (
            map_destinations["City"].astype(str)
            + ", "
            + map_destinations["State/Province"].astype(str)
            + ", "
            + map_destinations["Country/Region"].astype(str)
        )

        fig_map = px.scatter_geo(
            map_destinations,
            lat="Latitude",
            lon="Longitude",
            color="Marker_Status",
            color_discrete_map=status_colors,
            hover_name="Location",
            hover_data={
                "Coordinate_Type": True,
                "Latitude": ":.4f",
                "Longitude": ":.4f",
                "Marker_Status": True,
            },
            scope="north america",
            projection="natural earth",
            title="Customer destination coordinates",
        )

        factory_locations = (
            map_data[
                [
                    "Factory",
                    "Factory_Latitude",
                    "Factory_Longitude",
                ]
            ]
            .drop_duplicates(subset=["Factory"])
            .copy()
        )

        fig_map.add_scattergeo(
            lat=factory_locations["Factory_Latitude"],
            lon=factory_locations["Factory_Longitude"],
            text=factory_locations["Factory"],
            mode="markers+text",
            marker={
                "size": 10,
                "color": "#111827",
                "symbol": "star",
                "line": {"width": 1, "color": "white"},
            },
            textposition="top center",
            name="Factories",
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Latitude: %{lat:.4f}<br>"
                "Longitude: %{lon:.4f}"
                "<extra>Factory</extra>"
            ),
        )

        fig_map.update_layout(
            height=650,
            margin=dict(l=10, r=10, t=50, b=10),
            legend_title_text="Geocoding status",
        )

        st.plotly_chart(
            fig_map,
            width="stretch",
        )

        st.caption(
            "Destination markers represent distinct coordinate/status "
            "combinations. Overlapping locations may appear as one "
            "visible marker. Factory markers are shown as stars."
        )

        status_summary = (
            map_data.groupby("Lookup_Status", dropna=False)
            .agg(
                Order_Lines=("Order ID", "size"),
                Distinct_Destinations=("City", "nunique"),
            )
            .reset_index()
        )

        st.markdown("#### Coordinate status summary")
        st.dataframe(
            status_summary,
            hide_index=True,
            width="stretch",
        )
else:
    st.warning(
        "Distance file not found. Generate "
        "data/processed/factory_destination_distances.csv first."
    )


# --------------------------------------------------
# 8. Destination analysis tab
# --------------------------------------------------

with destination_tab:
    st.subheader("Customer destination analysis")

    st.caption(
        "Search destination records and examine the geographic "
        "distances associated with factory order lines."
    )

    search_text = st.text_input(
        "Search destination",
        placeholder=(
            "Enter a city, state, country, postal code, "
            "factory, or order ID"
        ),
        key="destination_search",
    )

    destination_data = filtered.copy()

    searchable_columns = [
        "City",
        "State/Province",
        "Country/Region",
        "Postal Code",
        "Factory",
        "Order ID",
        "Lookup_Status",
    ]

    if search_text.strip():
        search_mask = pd.Series(
            False,
            index=destination_data.index,
        )

        for column in searchable_columns:
            search_mask |= (
                destination_data[column]
                .fillna("")
                .astype(str)
                .str.contains(
                    search_text.strip(),
                    case=False,
                    regex=False,
                )
            )

        destination_data = destination_data.loc[
            search_mask
        ].copy()

    st.markdown("#### Matching records")

    st.metric(
        "Matching order lines",
        f"{len(destination_data):,}",
    )

    destination_columns = [
        "Order ID",
        "Factory",
        "City",
        "State/Province",
        "Postal Code",
        "Country/Region",
        "Lookup_Status",
        "Straight_Line_Distance_KM",
    ]

    st.dataframe(
        destination_data[destination_columns].rename(
            columns={
                "Order ID": "Order ID",
                "Factory": "Factory",
                "City": "City",
                "State/Province": "State / Province",
                "Postal Code": "Postal code",
                "Country/Region": "Country",
                "Lookup_Status": "Geocoding status",
                "Straight_Line_Distance_KM": (
                    "Straight-line distance (km)"
                ),
            }
        ).sort_values(
            "Straight-line distance (km)",
            ascending=False,
            na_position="last",
        ),
        width="stretch",
        hide_index=True,
        height=390,
    )

    st.divider()

    st.markdown("#### Longest estimated distances")

    valid_distances = destination_data.dropna(
        subset=["Straight_Line_Distance_KM"]
    )

    if not valid_distances.empty:
        longest = valid_distances.nlargest(
            15,
            "Straight_Line_Distance_KM",
        ).copy()

        longest["Distance_Rank"] = range(
            1,
            len(longest) + 1,
        )

        longest["Destination"] = (
            longest["City"].fillna("").astype(str)
            + ", "
            + longest["State/Province"].fillna("").astype(str)
            + ", "
            + longest["Country/Region"].fillna("").astype(str)
        )

        fig_longest = px.bar(
        longest.sort_values(
        "Straight_Line_Distance_KM",
        ascending=False,
        ),
        x="Destination",
        y="Straight_Line_Distance_KM",
        color="Factory",
        hover_data=[
        "Order ID",
        "Lookup_Status",
        ],
        labels={
        "Straight_Line_Distance_KM": "Distance (km)",
        "Destination": "Destination",
        "Factory": "Factory",
        },
        color_discrete_map=factory_colors,
)
        fig_longest.update_layout(
        height=540,
        margin=dict(l=20, r=20, t=20, b=130),
        xaxis_title="Destination",
        yaxis_title="Straight-line distance (km)",
        xaxis_tickangle=-45,
        legend_title="Factory",
      )

        st.plotly_chart(
            fig_longest,
            width="stretch",
        )

        st.caption(
            "These are the longest records in the current filtered "
            "data, not necessarily the longest actual truck routes. "
            "Unverified destination coordinates can affect rankings."
        )

        longest_columns = [
            "Distance_Rank",
            "Order ID",
            "Factory",
            "Destination",
            "Lookup_Status",
            "Straight_Line_Distance_KM",
        ]

        st.dataframe(
            longest[longest_columns].rename(
                columns={
                    "Distance_Rank": "Rank",
                    "Lookup_Status": "Geocoding status",
                    "Straight_Line_Distance_KM": "Distance (km)",
                }
            ),
            width="stretch",
            hide_index=True,
        )
    else:
        st.warning(
            "No valid distance records match the current search."
        )

    st.divider()

    st.markdown("#### Destination summary by city")

    city_summary = (
        destination_data.groupby(
            [
                "Country/Region",
                "State/Province",
                "City",
            ],
            dropna=False,
        )
        .agg(
            Order_Lines=("Order ID", "size"),
            Distinct_Orders=("Order ID", "nunique"),
            Factories=("Factory", "nunique"),
            Mean_Distance_KM=(
                "Straight_Line_Distance_KM",
                "mean",
            ),
        )
        .reset_index()
        .sort_values(
            "Order_Lines",
            ascending=False,
        )
    )

    city_summary["Mean_Distance_KM"] = (
        city_summary["Mean_Distance_KM"].round(2)
    )

    st.dataframe(
        city_summary.rename(
            columns={
                "Country/Region": "Country",
                "State/Province": "State / Province",
                "City": "City",
                "Order_Lines": "Order lines",
                "Distinct_Orders": "Distinct orders",
                "Factories": "Factories represented",
                "Mean_Distance_KM": "Mean distance (km)",
            }
        ),
        width="stretch",
        hide_index=True,
        height=350,
    )


# --------------------------------------------------
# 9. Data quality tab
# --------------------------------------------------

with quality_tab:
    st.subheader("Date Integrity Audit")

    st.warning(
        "Unresolved date anomaly: all 10,194 source records have "
        "Ship Date − Order Date differences greater than 365 days. "
        "The source dates have not been modified, and the cause has "
        "not been established. Treat shipping lead-time metrics as "
        "unverified until the source convention is clarified."
    )

    audit_cols = st.columns(4)

    audit_metrics = [
        ("Source records", "10,194"),
        ("Unparsed dates", "0"),
        ("Negative date gaps", "0"),
        ("Gaps over 365 days", "10,194"),
    ]

    for col, (label, value) in zip(audit_cols, audit_metrics):
        with col:
            st.metric(label, value)
    st.markdown("#### Date difference by Order ID year")

    date_audit = pd.DataFrame({
        "Order ID year": [2021, 2022, 2023, 2024],
        "Mean difference (days)": [
            908.07, 1273.07, 1272.95, 1638.83
        ],
        "Minimum (days)": [904, 1269, 1269, 1634],
        "Maximum (days)": [915, 1277, 1276, 1642],
    })

    st.dataframe(date_audit, hide_index=True, width="stretch")

    st.caption(
        "These figures describe differences between recorded dates, "
        "not verified real-world shipping durations. Values are from "
        "the source-data audit."
    )

    quality_data = filtered.copy()

    total_rows = len(quality_data)

    missing_distance = int(
        quality_data["Straight_Line_Distance_KM"].isna().sum()
    )

    valid_distance = int(
        quality_data["Straight_Line_Distance_KM"].notna().sum()
    )

    status_counts = (
        quality_data["Lookup_Status"]
        .fillna("Missing status")
        .astype(str)
        .value_counts()
        .rename_axis("Geocoding status")
        .reset_index(name="Order lines")
    )

    status_counts["Percentage"] = (
        status_counts["Order lines"] / total_rows * 100
        if total_rows
        else 0
    )

    q1, q2, q3 = st.columns(3)

    q1.metric("Filtered records", f"{total_rows:,}")
    q2.metric("Valid distance values", f"{valid_distance:,}")
    q3.metric("Missing distance values", f"{missing_distance:,}")

    st.divider()

    quality_left, quality_right = st.columns(2)

    with quality_left:
        st.markdown("#### Geocoding status distribution")

        fig_status = px.bar(
            status_counts,
            x="Geocoding status",
            y="Order lines",
            color="Geocoding status",
            text="Order lines",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={
                "Order lines": "Order lines",
            },
        )

        fig_status.update_traces(
            textposition="outside",
            cliponaxis=False,
        )

        fig_status.update_layout(
            showlegend=False,
            height=380,
            margin=dict(l=10, r=10, t=25, b=80),
            xaxis_tickangle=-25,
            xaxis_title="",
        )

        st.plotly_chart(
            fig_status,
            width="stretch",
        )

    with quality_right:
        st.markdown("#### Share of geocoding statuses")

        fig_status_pie = px.pie(
            status_counts,
            names="Geocoding status",
            values="Order lines",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )

        fig_status_pie.update_traces(
            textinfo="label+percent",
            textposition="inside",
        )

        fig_status_pie.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=25, b=10),
            showlegend=True,
        )

        st.plotly_chart(
            fig_status_pie,
            width="stretch",
        )

    st.markdown("#### Geocoding status details")

    st.dataframe(
        status_counts.round({"Percentage": 2}),
        width="stretch",
        hide_index=True,
    )

    st.info(
        "**Status interpretation:** “Found” does not mean "
        "independently verified. “Review” indicates records needing "
        "inspection. “Found_Canada_FSA” may use a postal-area "
        "representative point rather than an exact delivery address. "
        "“Retry_Found” should be interpreted according to the "
        "project's geocoding audit."
    )

    st.divider()

    st.markdown("#### Data validation checks")

    validation_rows = [
        {
            "Check": "Total filtered records",
            "Result": f"{total_rows:,}",
            "Interpretation": "Rows in the current filter selection",
        },
        {
            "Check": "Valid straight-line distances",
            "Result": f"{valid_distance:,}",
            "Interpretation": "Records with a numeric distance",
        },
        {
            "Check": "Missing straight-line distances",
            "Result": f"{missing_distance:,}",
            "Interpretation": "Cannot be used in distance statistics",
        },
        {
            "Check": "Unique order IDs",
            "Result": f"{quality_data['Order ID'].nunique():,}",
            "Interpretation": (
                "Distinct order identifiers in the filtered data"
            ),
        },
        {
            "Check": "Unique factories",
            "Result": f"{quality_data['Factory'].nunique():,}",
            "Interpretation": "Factories represented in the selection",
        },
    ]

    st.dataframe(
        pd.DataFrame(validation_rows),
        width="stretch",
        hide_index=True,
    )

    st.warning(
        "**Date anomaly still unresolved:** the source data contains "
        "order dates from 2024-01-02 to 2025-12-31 and ship dates "
        "from 2026-06-30 to 2030-06-28. This discrepancy must be "
        "investigated before using the dataset to report delivery "
        "lead times or shipping performance."
    )


# --------------------------------------------------
# 10. Methodology tab
# --------------------------------------------------

with methodology_tab:
    st.subheader("Methodology and research limitations")

    st.markdown("#### 1. Data source")

    st.write(
        "The analysis uses the project's processed factory-to-"
        "destination distance file. The original distributor dataset "
        "contains 10,194 rows and 18 columns, including order IDs, "
        "dates, factory assignments, customer destinations, sales, "
        "units, gross profit, and cost."
    )

    st.markdown("#### 2. Geographic distance calculation")

    st.write(
        "Distances are straight-line geographic estimates based on "
        "factory and destination coordinates. They approximate "
        "geographic separation, not the distance a vehicle travels "
        "on roads."
    )

    st.latex(
        r"d = 2R\\arcsin\\left("
        r"\\sqrt{\\sin^2\\left(\\frac{\\Delta\\phi}{2}\\right)"
        r"+\\cos(\\phi_1)\\cos(\\phi_2)"
        r"\\sin^2\\left(\\frac{\\Delta\\lambda}{2}\\right)}"
        r"\\right)"
    )

    st.write(
        "Here, d is the great-circle distance, R is the Earth's "
        "approximate radius, phi represents latitude, lambda "
        "represents longitude, and the deltas represent coordinate "
        "differences. This formula assumes spherical Earth geometry."
    )

    st.markdown("#### 3. Factory comparisons")

    st.write(
        "Factory comparisons summarize order-line volume, distinct "
        "orders, mean distance, median distance, and the observed "
        "distance range. A single order can contribute to multiple "
        "factory groups when its products are associated with "
        "different factories."
    )

    st.markdown("#### 4. Geocoding limitations")

    st.write(
        "Destination coordinates may be approximate, ambiguous, "
        "or unverified. Postal-area representative coordinates and "
        "records flagged for review can affect distance calculations "
        "and rankings. Factory assignments and factory coordinates "
        "also require confirmation against operational records."
    )

    st.markdown("#### 5. Date anomaly and lead times")

    st.write(
        "The order-date and ship-date ranges are inconsistent: "
        "the available ship dates are later than the order dates by "
        "a potentially substantial period. The cause has not been "
        "established. Do not interpret this as actual transit time, "
        "and do not publish lead-time or on-time-delivery conclusions "
        "until the date fields and source-system history are verified."
    )

    st.markdown("#### 6. What this dashboard can and cannot conclude")

    st.markdown(
        """
        **It can:**
        - Compare recorded order-line volumes by factory.
        - Summarize estimated geographic separation.
        - Identify records with long estimated distances.
        - Display geocoding-status distributions and missing distances.
        - Support further investigation of data quality.

        **It cannot establish from these fields alone:**
        - Actual road routes or driving distances.
        - Actual delivery times or on-time performance.
        - Fuel consumption, emissions, or shipping costs.
        - The optimal factory allocation or least-cost shipping plan.
        - The accuracy of every customer or factory coordinate.
        """
    )

    st.markdown("#### 7. Recommended next validation steps")

    st.markdown(
        """
        1. Investigate why the ship dates fall outside the expected
           period and verify the original date format and source.
        2. Review destination records marked `Review` and
           `Retry_Found`.
        3. Verify Canadian postal-area coordinates and factory
           locations against authoritative operational records.
        4. If route optimization is required, obtain road-network
           distances, transport constraints, shipment costs, and
           delivery requirements.
        5. Re-run the analysis after corrections and retain an audit
           of any changes.
        """
    )

    st.caption(
        "This dashboard is a descriptive geographic analysis. "
        "Conclusions should be updated only when supporting data "
        "has been validated."
    )


# --------------------------------------------------
# 11. Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Nassau Candy Distributor | Factory-to-Customer Shipping "
    "Distance Analysis | Descriptive estimates only"
)
