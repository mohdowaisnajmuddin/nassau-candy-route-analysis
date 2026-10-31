# Factory-to-Customer Shipping Route Efficiency Analysis Using the Nassau Candy Distributor Dataset

## Abstract

This study examines factory-to-customer geographic distribution patterns using the Nassau Candy Distributor dataset. The analysis covers 10,194 order-line records, representing 8,549 unique orders, five factories, and 1,386 factory-destination groups. The methodology includes data validation, product-to-factory mapping verification, destination geocoding, Haversine distance calculation, factory-level comparison, shipping-mode summaries, and route-investigation prioritization.

The factory-level analysis found differences in mean estimated straight-line distances across the five mapped factories. These averages were calculated using unique orders rather than product-line records. The analysis also identified destination records requiring geocoding review and approximate Canadian postal-area coordinates. An independent WGS84 geodesic calculation found that all 10,194 stored Haversine distances were within the project's 0.5% numerical tolerance.

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

5. Summarize order volume and commercial characteristics by shipping mode.

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

An independent implementation using the WGS84 geodesic calculation was used to validate the saved Haversine distances. Across 10,194 records, the mean absolute difference was 3.531 km, the median absolute difference was 2.860 km, and the maximum absolute difference was 10.833 km. The mean percentage difference was 0.163793%, and the maximum percentage difference was 0.323613%. All 10,194 records were within the project's 0.5% tolerance, with no records requiring distance-calculation review.

These results validate the mathematical consistency of the distance calculations, not the accuracy of the underlying coordinates or factory assignments.

### 4.5 Factory-destination analysis

Factory-destination distance statistics were calculated at the unique-order level. Before calculating order counts and mean estimated distances, duplicate product-line records were removed using Order ID as the unique identifier. Product-line volume was retained and reported separately as Order_Lines, while the number of unique orders was reported as Distinct_Orders. This prevents orders containing multiple product lines from receiving disproportionate weight in order-level distance summaries.

### 4.6 Route-investigation prioritization

The high-volume threshold was defined using the 75th percentile of **Distinct_Orders**, producing a threshold of 5 unique orders per factory-destination group. Groups with at least 5 distinct orders were classified as high-volume groups. This order-level measure avoids giving extra weight to destinations simply because an order contains multiple product lines.

### 4.7 Shipping-mode analysis

Shipping mode was joined to the distance dataset using Row ID. All 10,194 records matched, with no unmatched rows. Order-line volume and estimated straight-line distance were summarized for First Class, Same Day, Second Class, and Standard Class.

The results are descriptive comparisons only. They do not establish that one shipping mode delivers faster or more efficiently than another.

## 5. Results

### 5.1 Factory-level geographic distribution

The order-consistency audit found that each of the 8,549 unique orders maps to exactly one factory. Therefore, factory-level distinct-order counts sum to 8,549 in this audited dataset. This describes the supplied product-to-factory mapping and does not independently verify the physical dispatch location.
Factory	Order lines	Distinct orders	Mean estimated distance (km)
Lot's O' Nuts	5,692	4,760	2,140.14
Wicked Choccy's	4,152	3,445	1,871.74
Sugar Shack	33	33	1,797.32
The Other Factory	100	98	1,631.09
Secret Factory	217	213	1,440.29


Distance averages are order-weighted: each unique order contributes once. Order-line counts are shown separately and should not be interpreted as the denominator for the distance averages.

### 5.2 Shipping-mode comparison



| Shipping mode | Distinct orders | Order share | Average order value (USD) | Gross margin |
|---|---:|---:|---:|---:|
| Standard Class | 5,142 | 60.15% | $16.63 | 66.00% |
| Second Class | 1,653 | 19.34% | $16.85 | 65.71% |
| First Class | 1,312 | 15.35% | $16.25 | 65.72% |
| Same Day | 442 | 5.17% | $16.09 | 66.08% |
| **Total** | **8,549** | **100.00%** | | |

Standard Class represents the largest share of orders, accounting for 60.15% of the 8,549 unique orders. Second Class accounts for 19.34%, First Class for 15.35%, and Same Day for 5.17%. Average order values range from $16.09 to $16.85, while gross margins range from 65.71% to 66.08%. These results describe order distribution and commercial characteristics across ship modes. They do not establish differences in delivery speed, transit reliability, or shipping cost efficiency because reliable transit durations and shipping charges are unavailable in the dataset.

### 5.3 Route-investigation priorities

The 1,386 factory-destination groups were classified using distinct-order volume, estimated straight-line distance, and coordinate-quality flags. The 75th-percentile thresholds were 5 distinct orders and 2,711.32 km. Categories follow a priority order: missing distances, ambiguous geocoding, approximate Canadian postal-area coordinates, retry-found coordinates, high volume combined with long distance, high volume, long estimated distance, and routine screening. Because coordinate-review categories take precedence, some groups that also meet volume or distance thresholds appear under a coordinate-review category. These classifications identify groups for further investigation; they do not demonstrate delivery delays, poor shipping performance, or operational bottlenecks.
Priority category	Factory-destination groups
Routine screening	703
High volume	275
Long estimated distance	213
High volume + long estimated distance	112
Ambiguous geocoding review	55
Approximate Canadian postal-area coordinates	20
Retry-found coordinates to verify	8
Total	1,386


### 5.4 Geographic-data quality

The processed dataset contains no missing or negative distance values. All 10,194 distance records were compared with an independent WGS84 geodesic calculation and passed the project's 0.5% numerical tolerance checks.

However, 712 order-line records have ambiguous geocoding status, 88 use approximate Canadian postal-area coordinates, and 19 were found after retry. These records require different levels of verification before the results can be used for detailed logistics decisions.

The interactive map displays customer coordinates and factory markers to support geographic exploration. It is a location map rather than a road-routing map.

### 5.5 Date anomaly

Order dates range from 2 January 2024 to 31 December 2025. Ship dates range from 30 June 2026 to 28 June 2030. Both date columns were successfully parsed, with no parsing failures and no records where the ship date precedes the order date.

However, all 10,194 records show a recorded order-to-ship interval greater than 365 days. The interval ranges from 904 to 1,642 days, with a mean of 1,320.84 days and a median of 1,274 days.

The underlying cause could not be established from the available evidence. The working file and the compared public reference copy contain matching order-date and ship-date values across all 10,194 records. This confirms agreement between the compared copies, but does not establish which dates, if any, are incorrect or explain the anomaly.

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

## Dashboard implementation and requirement limitations

The Streamlit dashboard supports filtering by factory, geocoding status, country, geographic-validation result, customer region, ship mode, and recorded order-date range. Region, ship mode, and date attributes are joined from the original source dataset at the unique-order level after checking that each Order ID has consistent values for those attributes.

The order-date filter is provided for historical record exploration only. It must not be interpreted as a delivery-performance filter because all 10,194 recorded order-to-ship intervals exceed 365 days and the cause of the anomaly remains unknown. A lead-time threshold slider, delay-frequency KPI, lead-time ranking, and delivery-efficiency score are therefore not implemented. Likewise, order-level date displays must be understood as recorded source values, not verified shipment timelines. The existing state-level selector supports geographic drill-down, while straight-line distance remains a screening measure rather than road-route distance.

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