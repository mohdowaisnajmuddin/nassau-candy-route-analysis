# Factory-to-Customer Shipping Route Efficiency Analysis Using the Nassau Candy Distributor Dataset

## Abstract

This study examines factory-to-customer geographic distribution patterns using the Nassau Candy Distributor dataset. The analysis covers 10,194 order-line records, representing 8,549 unique orders, five factories, and 1,386 factory-destination groups. The methodology includes data validation, product-to-factory mapping verification, destination geocoding, Haversine distance calculation, factory-level comparison, shipping-mode summaries, and route-investigation prioritization.

The mean estimated straight-line distance across factory-destination groups varies by factory. Lot's O' Nuts has a mean distance of 2,145.50 km, while Secret Factory has a mean of 1,437.03 km. The analysis also identifies destination records requiring geocoding review and approximate Canadian postal-area coordinates. An independent calculation confirms that the stored geographic distances are mathematically consistent with the Haversine formula.

A significant limitation concerns the date fields: all 10,194 records have recorded order-to-ship intervals exceeding 365 days. The underlying cause could not be established from the available evidence. Consequently, these intervals are not treated as validated delivery times. The findings support geographic distribution analysis and further investigation, but do not establish actual transportation efficiency, road distance, or delivery speed.

**Keywords:** Supply chain analytics, geographic distance, Haversine formula, route analysis, data quality, Streamlit, Python, distribution networks.

## 1. Introduction

Efficient distribution is important for organizations that transport products from manufacturing facilities to customers across different geographic regions. Understanding the geographic separation between factories and customer destinations can help identify locations for further logistics investigation and support distribution-network planning.

This project analyzes the Nassau Candy Distributor dataset to examine factory-to-customer geographic distances, destination concentration, product-to-factory assignments, and data-quality concerns. Python and its data-analysis libraries are used to prepare and validate the data, calculate straight-line distances, generate analytical reports, and develop an interactive Streamlit dashboard.

The project distinguishes between geographic distance estimates and actual shipping performance. The available dataset does not provide independently verified road routes or reliable delivery-time measurements, and its date fields contain a systematic anomaly.

## 2. Objectives

The main objectives are:

1. Validate the structure and consistency of the source dataset.
2. Verify that the 15 specified products are assigned to their expected factories.
3. Estimate straight-line geographic distances between factories and customer destinations.
4. Compare geographic distribution patterns across the five factories.
5. Summarize estimated distances and order-line volumes by shipping mode.
6. Prioritize factory-destination groups for further investigation.
7. Examine geocoding uncertainty and other data-quality limitations.
8. Build an interactive dashboard for exploring the results.

## 3. Dataset Description

The dataset contains 10,194 order-line records and 18 columns, including order identifiers, order and ship dates, shipping mode, customer location, product information, sales, units, gross profit, and cost.

| Attribute | Recorded result |
|---|---:|
| Order-line records | 10,194 |
| Unique orders | 8,549 |
| Product names | 15 |
| Factories | 5 |
| Factory-destination groups | 1,386 |
| Missing source date values | 0 |
| Duplicate Row IDs | 0 |

The five factories are Lot's O' Nuts, Wicked Choccy's, Sugar Shack, Secret Factory, and The Other Factory.

The dataset was obtained through the project source supplied by Unified Mentor. A comparison with a public GitHub copy found matching row counts, columns, and date values across all 10,194 records. This agreement confirms consistency between those copies, but does not independently establish the historical accuracy of the dataset.

## 4. Methodology

### 4.1 Data validation and preparation

The source CSV was inspected for missing values, duplicate row identifiers, date-parsing failures, and inconsistencies. Processed records were matched using Row ID. The source and geographic-distance datasets both contained 10,194 rows, with no missing or duplicate Row IDs and no unmatched identifiers.

The original date values were preserved. No unsupported corrections were applied.

### 4.2 Product-to-factory mapping

The dataset's 15 product names were checked against the factory assignments supplied in the project specification. Validation found no missing product names, unexpected products, or incorrect or incomplete assignments.

This confirms agreement with the supplied mapping specification; it does not independently verify the physical manufacturing or dispatch location of each product.

### 4.3 Destination geocoding

Customer destinations were assigned geographic coordinates using the project's geocoding workflow. The processed dataset records the lookup status so that approximate, ambiguous, and retry-found coordinates can be distinguished from standard geocoding results.

The final record-level status counts were:

| Geocoding status | Order lines | Share |
|---|---:|---:|
| Found | 9,375 | 91.97% |
| Found_Canada_FSA | 88 | 0.86% |
| Retry_Found | 19 | 0.19% |
| Review | 712 | 6.98% |
| **Total** | **10,194** | **100%** |

Canadian FSA coordinates represent approximate postal-area locations rather than exact delivery addresses. Review status indicates that multiple candidate locations were returned and require additional scrutiny. A successful lookup alone does not guarantee coordinate accuracy.

### 4.4 Haversine distance calculation

Straight-line geographic distance was calculated using the Haversine formula, which estimates the great-circle distance between two points on a spherical approximation of Earth.

For latitudes \(\phi_1,\phi_2\) and longitudes \(\lambda_1,\lambda_2\), expressed in radians:

\[
a=\sin^2\left(\frac{\phi_2-\phi_1}{2}\right)
+\cos(\phi_1)\cos(\phi_2)
\sin^2\left(\frac{\lambda_2-\lambda_1}{2}\right)
\]

\[
d=2R\arcsin(\sqrt{a})
\]

where \(R=6,371\) km and \(d\) is the estimated straight-line distance.

An independent implementation was used to validate the saved distances. The mean absolute difference was approximately 0.0028 km, and the maximum absolute difference was approximately 0.0071 km. No record differed by more than 0.01 km or 1 km.

These results validate the mathematical consistency of the calculations, not the accuracy of the underlying coordinates or factory assignments.

### 4.5 Factory-destination analysis

Records were grouped by factory, country or region, state or province, city, and postal code. The resulting 1,386 groups were summarized using order-line counts, distinct-order counts, mean distance, median distance, maximum distance, and geocoding-quality indicators.

### 4.6 Route-investigation prioritization

Factory-destination groups were prioritized using order-line volume, estimated geographic distance, and coordinate-quality flags. The 75th-percentile thresholds were six order lines and 2,711.32 km.

The categories are screening labels designed to guide further investigation. They do not measure transportation efficiency or prove that a route is operationally inefficient.

### 4.7 Shipping-mode analysis

Shipping mode was joined to the distance dataset using Row ID. All 10,194 records matched, with no unmatched rows. Order-line volume and estimated straight-line distance were summarized for First Class, Same Day, Second Class, and Standard Class.

The results are descriptive comparisons only. They do not establish that one shipping mode delivers faster or more efficiently than another.

## 5. Results

### 5.1 Factory-level geographic distribution

| Factory | Order lines | Distinct orders | Mean distance (km) |
|---|---:|---:|---:|
| Lot's O' Nuts | 5,692 | 4,760 | 2,145.50 |
| Wicked Choccy's | 4,152 | 3,445 | 1,863.23 |
| Sugar Shack | 33 | 33 | 1,797.32 |
| The Other Factory | 100 | 98 | 1,643.91 |
| Secret Factory | 217 | 213 | 1,437.03 |

Lot's O' Nuts has the highest mean estimated straight-line distance among the five factories, while Secret Factory has the lowest. Lot's O' Nuts and Wicked Choccy's account for most of the order-line records.

These differences describe the geographic distribution of the recorded destinations associated with each factory. They should not be interpreted as evidence that one factory has higher transportation costs, longer road journeys, or poorer delivery performance.

Distinct-order counts are reported within each factory. An order may involve more than one factory, so factory-level counts should not automatically be summed to derive a global number of unique orders.

### 5.2 Shipping-mode comparison

| Shipping mode | Order lines | Distinct orders | Mean distance (km) | Median distance (km) |
|---|---:|---:|---:|---:|
| First Class | 1,548 | 1,312 | 2,016.96 | 1,730.12 |
| Same Day | 547 | 442 | 1,990.28 | 1,718.06 |
| Second Class | 1,979 | 1,653 | 2,013.10 | 1,774.92 |
| Standard Class | 6,120 | 5,142 | 2,008.00 | 1,690.13 |

Standard Class accounts for the largest number of order lines. Mean estimated distance is relatively similar across all four shipping modes.

These values do not measure delivery speed. The recorded date anomaly prevents reliable interpretation of order-to-ship intervals, and straight-line distance is not a substitute for road distance or actual transportation time.

### 5.3 Route-investigation priorities

The priority analysis classified all 1,386 factory-destination groups into mutually exclusive categories.

| Investigation category | Groups |
|---|---:|
| Routine screening | 715 |
| High volume | 263 |
| Long estimated distance | 217 |
| High volume + long estimated distance | 108 |
| Ambiguous geocoding review | 55 |
| Approximate Canadian postal-area coordinates | 20 |
| Retry-found coordinates to verify | 8 |
| **Total** | **1,386** |

The categories involving high volume or long distance can help identify destinations worth examining after data-quality issues are considered. The geocoding categories highlight groups where coordinate verification may be more important than ranking the destination by distance.

The category precedence means that a group assigned to a geocoding-review category is not also counted in the high-volume or long-distance categories, even if it meets those thresholds.

### 5.4 Geographic-data quality

The processed dataset contains no missing or negative distance values. All 10,194 distance records were compared with an independent Haversine calculation and passed the project's numerical tolerance checks.

However, 712 order-line records have ambiguous geocoding status, 88 use approximate Canadian postal-area coordinates, and 19 were found after retry. These records require different levels of verification before the results can be used for detailed logistics decisions.

The interactive map displays customer coordinates and factory markers to support geographic exploration. It is a location map rather than a road-routing map.

### 5.5 Date anomaly

Order dates range from 2 January 2024 to 31 December 2025. Ship dates range from 30 June 2026 to 28 June 2030. Both date columns were successfully parsed, with no parsing failures and no records where the ship date precedes the order date.

However, all 10,194 records show a recorded order-to-ship interval greater than 365 days. The interval ranges from 904 to 1,642 days, with a mean of 1,320.84 days and a median of 1,274 days.

The underlying cause could not be established from the available evidence. The working file and a public reference copy contain matching dates, and an initial comparison with the downloaded project-source file also found matching row counts, columns, and sample date values.

The original dates were preserved. No year substitutions or modulo-based date corrections were applied because no independently validated correction method was available.

Accordingly, these values are treated as anomalous recorded date intervals rather than validated shipping lead times. No conclusions about actual delivery speed, delivery timeliness, or shipping-mode performance are drawn from them.

## 6. Discussion

The results demonstrate that geographic-distance analysis can be used to describe the recorded distribution network and identify factory-destination groups for further investigation. The concentration of order lines around two factories suggests that these factories and their associated destinations deserve particular attention when reviewing the geographic structure of the dataset.

Distance-based screening may be useful for identifying destinations that merit further logistical assessment. However, straight-line distance alone cannot establish whether a route is inefficient. Actual transportation performance also depends on road networks, dispatch practices, vehicle capacity, shipment consolidation, delivery schedules, and other operational factors not established by this analysis.

The geocoding-quality results further demonstrate why data-quality checks should accompany geographic analysis. Approximate and ambiguous coordinates can affect distance estimates and the ranking of destinations. Such records should be verified before being used for high-impact operational decisions.

Finally, the date anomaly limits the conclusions that can be drawn from shipping dates. A valid analysis of delivery performance would require reliable order, dispatch, and delivery timestamps with a documented and defensible interpretation.

## 7. Limitations

1. **Unresolved date anomaly:** All recorded order-to-ship intervals exceed 365 days. Their cause remains unknown.
2. **Straight-line distances:** The Haversine calculation does not account for roads, traffic, borders, or actual travel paths.
3. **Coordinate accuracy:** Numerical validation of distances does not prove that destination coordinates are correct.
4. **Approximate Canadian locations:** Some Canadian coordinates represent postal-area centroids or representative areas rather than exact delivery addresses.
5. **Ambiguous geocoding:** Multiple returned candidates require further verification.
6. **Factory mapping:** Product assignments were checked against the supplied specification, not independently verified against operational dispatch records.
7. **No verified transportation costs:** The analysis does not establish fuel, labor, toll, or route-specific delivery costs.
8. **No causal evaluation:** Differences between factories or shipping modes are descriptive and do not prove operational causes or performance differences.
9. **Source provenance:** Matching dataset copies establish consistency between files, but do not independently establish the dataset's original collection process or historical accuracy.

## 8. Recommendations

1. Obtain clarification from the dataset provider regarding the order-date and ship-date anomaly before conducting delivery-time analysis.
2. Preserve the original date columns and document any future correction with source evidence, an explicit method, and validation checks.
3. Review the ambiguous geocoding records and confirm approximate Canadian postal-area coordinates where greater precision is required.
4. Use the route-priority report as a screening tool for further investigation rather than a final ranking of inefficient routes.
5. If operational routing is the goal, obtain road-network distances or route estimates from a validated routing service.
6. If transportation efficiency is the goal, collect verified dispatch and delivery timestamps, actual transportation costs, and relevant operational measures.
7. Maintain reproducible scripts, validation reports, and data-quality documentation so that the analysis can be rerun and audited.
8. Use the interactive dashboard to explore geographic patterns while clearly communicating the limits of the available evidence.

## 9. Conclusion

This project developed a reproducible workflow for examining factory-to-customer geographic distribution using the Nassau Candy Distributor dataset. The workflow validated 10,194 order-line records, checked the five-factory product mapping, calculated straight-line distances for 1,386 factory-destination groups, summarized shipping modes, and generated a route-investigation priority report and interactive dashboard.

The findings show differences in estimated geographic distance across factories and identify destination groups that merit additional review. Independent numerical checks support the mathematical consistency of the Haversine calculations, while geocoding-status analysis highlights remaining uncertainty in some coordinates.

The principal limitation is the unresolved date anomaly. Since every recorded order-to-ship interval exceeds 365 days, the available data does not support reliable conclusions about actual delivery times or shipping efficiency. The project should therefore be understood as a geographic distribution and data-quality analysis, providing a foundation for further investigation when validated operational data becomes available.

## Appendix A: Project technologies

- Python
- pandas and NumPy for data processing and calculations
- Haversine distance calculations
- Geocoding and coordinate-quality checks
- Plotly for interactive charts and geographic visualization
- Streamlit for the dashboard
- CSV-based intermediate datasets and analytical reports

## Appendix B: Reproducibility and validation

The project includes scripts for data cleaning, date-anomaly investigation, destination geocoding, distance calculation, route analysis, route-priority generation, shipping-mode analysis, and final structural validation.

The final structural validation confirmed matching source and processed row counts, unique and complete Row IDs, no missing or negative distances, route-report order-line totals matching the source, and shipping-mode order-line totals matching the source.

These checks establish internal structural and computational consistency. They do not resolve the date anomaly or independently prove the accuracy of all underlying geographic locations.

## References and source notes

1. Unified Mentor, project instructions and source dataset provided for *Factory-to-Customer Shipping Route Efficiency Analysis*. Project instructions: https://projects.unifiedmentor.com/project_instructions?id=27265
2. Public reference copy used for dataset consistency checks: https://github.com/Prasannasegabandi36/Nassau-Candy-Distributor
3. Haversine formula: standard spherical-geometry method for estimating great-circle distance from latitude and longitude coordinates.

**Citation note:** The project dataset and project instructions are the primary materials used for the analysis. The public reference copy was used to check consistency, not to independently establish the accuracy of the underlying records. The unresolved date anomaly should not be described as corrected or explained without further authoritative evidence.