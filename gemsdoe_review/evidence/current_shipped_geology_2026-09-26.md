# Geological hypotheses for the current model's flagged components

**Raster:** `gems6_hgb88-topk03_33cec71ff0.tif`; SHA-256 `33cec71ff00b3f32d0d59c81c156f3f1488ffef46baa4b6499094e24ea1875ab`. This is a pixel prediction, **not an expert-verified fault map or a leaderboard result**.
**Method:** 5×5-pixel morphological closing of 131,416 off-catalogue positive pixels produced 2,589 components. The 180 at ≥200 closed pixels are reviewed below, **all 180** (not just the top ten). The remaining 2,409 smaller components have not been geologically interpreted and must not be called discovered faults. All are accounted for in the [fragment inventory](current_shipped_geology_fragments_2026-09-26.csv) (26,040 emitted px, each assessed 'not an identified fault by this screen'). A further 93 off-catalogue emitted px were not retained by closing and were not assigned to a component (the grid boundary can cause this).
Class is a **distance heuristic**, not a geological label: 1 isolated, 87 near a mapped trace, 92 mapped-trace halos. The closed component defines groups/PCA and can contain non-predicted bridging pixels; band summaries and mapped-trace distances use **emitted, off-catalogue pixels** only.

Signals are medians over emitted pixels expressed as regional percentiles of all-band-valid locations on the pinned 100 m feature raster ([official band descriptions](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features)); 90th/10th-percentile thresholds are descriptive, not validated likelihoods. Magnetic gradients and gravity gradients may be lithological contacts; slope breaks may be erosional; strain and earthquake layers may describe broad zones; conductivity can reflect lithology as well as fluids. The supplied magnetic tilt is not calibrated to derive depth and is excluded from agreement. None of the six families is asserted to be statistically independent of the others.

The [official metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) uses a 300 m kernel, while [DrivenData staff](https://community.drivendata.org/t/11516/4) clarified that the known-fault mask is **pixel-exact**, not buffered: a correction may be within 300 m of a known trace, but a halo with no new fault is penalized. [Staff also declined to disclose test-fault sources, types, or coverage](https://community.drivendata.org/t/11527/7). Do not use this page to assert those unknowns.

The [official study context](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/#about-the-data) mentions the Walker Lane and western Great Basin, but NO individual component is assigned to a specific fault system or regime from PCA orientation alone. PCA strike is an axis, not a verified fault trend. Original 1 m DEM/field observations and a mapped system-level geologist review are required to choose between each hypothesis and its counterexample. **No depth estimates are offered.**

## Assessments (every ≥200 px component)

### S-001 · component 2353 (near_trace; 16,752 closed / 11,580 emitted px)
Centroid 38.0385°N, 118.4689°W; PCA axis azimuth 98.2° clockwise from north, elongation 3.4:1, axes 29.1 × 8.6 km. Median distance to mapped trace 224 m; 62.7% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.97 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 1.00 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.4:1; minor axis 8.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-002 · component 2460 (near_trace; 12,633 closed / 8,914 emitted px)
Centroid 37.6516°N, 118.0679°W; PCA axis azimuth 149.4° clockwise from north, elongation 9.8:1, axes 70.3 × 7.2 km. Median distance to mapped trace 224 m; 62.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (9.8:1; minor axis 7.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-003 · component 2217 (near_trace; 8,518 closed / 5,397 emitted px)
Centroid 38.4384°N, 117.8559°W; PCA axis azimuth 175.1° clockwise from north, elongation 1.8:1, axes 18.6 × 10.4 km. Median distance to mapped trace 200 m; 69.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 10.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-004 · component 1293 (halo; 6,679 closed / 4,596 emitted px)
Centroid 39.6639°N, 118.1646°W; PCA axis azimuth 12.2° clockwise from north, elongation 5.2:1, axes 34.5 × 6.6 km. Median distance to mapped trace 200 m; 78.4% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (5.2:1; minor axis 6.6 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-005 · component 1213 (near_trace; 4,712 closed / 4,061 emitted px)
Centroid 39.8056°N, 118.4591°W; PCA axis azimuth 17.2° clockwise from north, elongation 2.0:1, axes 11.3 × 5.7 km. Median distance to mapped trace 224 m; 60.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 5.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-006 · component 2419 (near_trace; 3,502 closed / 2,271 emitted px)
Centroid 37.8638°N, 117.9152°W; PCA axis azimuth 22.6° clockwise from north, elongation 2.9:1, axes 18.5 × 6.4 km. Median distance to mapped trace 200 m; 73.3% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 6.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-007 · component 292 (near_trace; 3,154 closed / 2,486 emitted px)
Centroid 40.4206°N, 119.1217°W; PCA axis azimuth 13.1° clockwise from north, elongation 2.0:1, axes 9.7 × 4.9 km. Median distance to mapped trace 224 m; 62.1% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 4.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-008 · component 1578 (near_trace; 2,792 closed / 1,751 emitted px)
Centroid 39.4036°N, 118.2369°W; PCA axis azimuth 79.4° clockwise from north, elongation 2.6:1, axes 14.5 × 5.6 km. Median distance to mapped trace 200 m; 70.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 5.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-009 · component 2360 (near_trace; 2,511 closed / 1,761 emitted px)
Centroid 38.0200°N, 117.5890°W; PCA axis azimuth 46.3° clockwise from north, elongation 3.8:1, axes 14.4 × 3.8 km. Median distance to mapped trace 200 m; 72.1% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.95 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.8:1; minor axis 3.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-010 · component 146 (near_trace; 2,354 closed / 1,424 emitted px)
Centroid 40.5027°N, 118.2475°W; PCA axis azimuth 4.7° clockwise from north, elongation 9.1:1, axes 28.2 × 3.1 km. Median distance to mapped trace 200 m; 70.0% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.93 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.06 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (9.1:1; minor axis 3.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-011 · component 795 (near_trace; 2,337 closed / 1,575 emitted px)
Centroid 40.1207°N, 118.7380°W; PCA axis azimuth 72.8° clockwise from north, elongation 1.1:1, axes 7.7 × 7.0 km. Median distance to mapped trace 283 m; 55.6% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.08 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 7.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-012 · component 166 (near_trace; 1,661 closed / 974 emitted px)
Centroid 40.5805°N, 116.8299°W; PCA axis azimuth 96.7° clockwise from north, elongation 1.7:1, axes 7.3 × 4.2 km. Median distance to mapped trace 200 m; 72.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 4.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-013 · component 1255 (halo; 1,507 closed / 1,214 emitted px)
Centroid 39.7865°N, 118.6759°W; PCA axis azimuth 61.5° clockwise from north, elongation 2.5:1, axes 7.1 × 2.9 km. Median distance to mapped trace 200 m; 77.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-014 · component 2076 (halo; 1,477 closed / 893 emitted px)
Centroid 38.6579°N, 118.1114°W; PCA axis azimuth 158.4° clockwise from north, elongation 3.7:1, axes 10.3 × 2.8 km. Median distance to mapped trace 141 m; 81.5% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.92 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.96 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.94 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (3.7:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-015 · component 2162 (near_trace; 1,415 closed / 1,077 emitted px)
Centroid 38.5241°N, 118.6794°W; PCA axis azimuth 156.8° clockwise from north, elongation 10.0:1, axes 15.3 × 1.5 km. Median distance to mapped trace 224 m; 68.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-016 · component 1116 (near_trace; 1,380 closed / 878 emitted px)
Centroid 39.8983°N, 119.7523°W; PCA axis azimuth 173.0° clockwise from north, elongation 2.5:1, axes 9.9 × 4.0 km. Median distance to mapped trace 224 m; 61.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 4.0 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-017 · component 2127 (halo; 1,335 closed / 865 emitted px)
Centroid 38.6013°N, 117.9934°W; PCA axis azimuth 160.0° clockwise from north, elongation 4.3:1, axes 11.7 × 2.7 km. Median distance to mapped trace 200 m; 75.0% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (4.3:1; minor axis 2.7 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-018 · component 606 (near_trace; 1,308 closed / 813 emitted px)
Centroid 40.2034°N, 118.7495°W; PCA axis azimuth 161.0° clockwise from north, elongation 2.4:1, axes 8.5 × 3.5 km. Median distance to mapped trace 224 m; 61.0% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.00 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 3.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-019 · component 2548 (near_trace; 1,291 closed / 731 emitted px)
Centroid 37.6376°N, 117.4500°W; PCA axis azimuth 23.4° clockwise from north, elongation 3.5:1, axes 10.9 × 3.1 km. Median distance to mapped trace 200 m; 65.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.5:1; minor axis 3.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-020 · component 1661 (near_trace; 1,256 closed / 805 emitted px)
Centroid 39.3438°N, 118.1837°W; PCA axis azimuth 29.3° clockwise from north, elongation 2.2:1, axes 7.4 × 3.3 km. Median distance to mapped trace 200 m; 73.4% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 3.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-021 · component 678 (near_trace; 1,251 closed / 886 emitted px)
Centroid 40.1537°N, 116.5890°W; PCA axis azimuth 178.8° clockwise from north, elongation 5.1:1, axes 19.4 × 3.8 km. Median distance to mapped trace 200 m; 74.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median), gravity-gradient/density boundary (grav_hgm, high 0.95 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.02 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.1:1; minor axis 3.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-022 · component 109 (halo; 1,219 closed / 908 emitted px)
Centroid 40.5956°N, 116.7577°W; PCA axis azimuth 10.1° clockwise from north, elongation 4.4:1, axes 20.2 × 4.6 km. Median distance to mapped trace 200 m; 86.7% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (4.4:1; minor axis 4.6 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-023 · component 2140 (halo; 1,205 closed / 868 emitted px)
Centroid 38.5594°N, 118.0456°W; PCA axis azimuth 160.1° clockwise from north, elongation 3.4:1, axes 12.3 × 3.7 km. Median distance to mapped trace 200 m; 78.5% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.96 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (3.4:1; minor axis 3.7 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-024 · component 2106 (near_trace; 1,160 closed / 583 emitted px)
Centroid 38.6368°N, 118.4684°W; PCA axis azimuth 100.1° clockwise from north, elongation 2.0:1, axes 7.8 × 4.0 km. Median distance to mapped trace 200 m; 71.2% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.97 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.98 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 4.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-025 · component 1373 (near_trace; 1,158 closed / 611 emitted px)
Centroid 39.6463°N, 119.0442°W; PCA axis azimuth 33.0° clockwise from north, elongation 1.6:1, axes 7.0 × 4.4 km. Median distance to mapped trace 283 m; 55.8% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 4.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-026 · component 1317 (near_trace; 1,129 closed / 708 emitted px)
Centroid 39.7210°N, 119.3381°W; PCA axis azimuth 146.6° clockwise from north, elongation 2.4:1, axes 7.0 × 3.0 km. Median distance to mapped trace 200 m; 74.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 3.0 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-027 · component 2268 (near_trace; 1,082 closed / 569 emitted px)
Centroid 38.4393°N, 118.6225°W; PCA axis azimuth 135.4° clockwise from north, elongation 2.1:1, axes 6.2 × 3.0 km. Median distance to mapped trace 200 m; 72.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.99 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 3.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-028 · component 319 (halo; 1,066 closed / 798 emitted px)
Centroid 40.3941°N, 117.4678°W; PCA axis azimuth 7.9° clockwise from north, elongation 10.3:1, axes 17.4 × 1.7 km. Median distance to mapped trace 200 m; 76.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-029 · component 953 (near_trace; 1,066 closed / 673 emitted px)
Centroid 40.0538°N, 118.8114°W; PCA axis azimuth 12.7° clockwise from north, elongation 2.7:1, axes 6.5 × 2.4 km. Median distance to mapped trace 224 m; 64.8% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-030 · component 469 (halo; 1,041 closed / 857 emitted px)
Centroid 40.2965°N, 116.4635°W; PCA axis azimuth 52.4° clockwise from north, elongation 14.2:1, axes 23.6 × 1.7 km. Median distance to mapped trace 200 m; 80.2% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-031 · component 1970 (halo; 1,041 closed / 664 emitted px)
Centroid 38.8764°N, 118.2450°W; PCA axis azimuth 60.2° clockwise from north, elongation 2.5:1, axes 6.3 × 2.6 km. Median distance to mapped trace 141 m; 81.6% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.99 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-032 · component 2347 (near_trace; 1,002 closed / 636 emitted px)
Centroid 38.1047°N, 117.8851°W; PCA axis azimuth 178.3° clockwise from north, elongation 4.0:1, axes 8.4 × 2.1 km. Median distance to mapped trace 200 m; 66.7% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.0:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-033 · component 2517 (near_trace; 985 closed / 497 emitted px)
Centroid 37.6990°N, 117.4152°W; PCA axis azimuth 30.2° clockwise from north, elongation 2.4:1, axes 6.2 × 2.6 km. Median distance to mapped trace 224 m; 61.6% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-034 · component 1735 (halo; 956 closed / 654 emitted px)
Centroid 39.2271°N, 118.1412°W; PCA axis azimuth 8.5° clockwise from north, elongation 12.4:1, axes 18.4 × 1.5 km. Median distance to mapped trace 200 m; 75.5% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.92 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.97 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-035 · component 1731 (halo; 949 closed / 669 emitted px)
Centroid 39.2386°N, 118.3279°W; PCA axis azimuth 5.0° clockwise from north, elongation 9.4:1, axes 18.9 × 2.0 km. Median distance to mapped trace 200 m; 77.1% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.97 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.95 regional percentile of the component median), geodetic shear rate (geod_shearrate, high 0.90 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (9.4:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-036 · component 135 (near_trace; 933 closed / 618 emitted px)
Centroid 40.6095°N, 117.6218°W; PCA axis azimuth 173.8° clockwise from north, elongation 4.4:1, axes 8.3 × 1.9 km. Median distance to mapped trace 400 m; 44.2% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-037 · component 1594 (halo; 914 closed / 589 emitted px)
Centroid 39.3620°N, 118.0714°W; PCA axis azimuth 7.7° clockwise from north, elongation 9.2:1, axes 14.7 × 1.6 km. Median distance to mapped trace 200 m; 79.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-038 · component 262 (halo; 908 closed / 606 emitted px)
Centroid 40.4658°N, 117.5343°W; PCA axis azimuth 171.8° clockwise from north, elongation 5.0:1, axes 13.1 × 2.6 km. Median distance to mapped trace 200 m; 80.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (5.0:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-039 · component 1181 (near_trace; 891 closed / 628 emitted px)
Centroid 39.8480°N, 118.0310°W; PCA axis azimuth 22.4° clockwise from north, elongation 4.9:1, axes 13.1 × 2.7 km. Median distance to mapped trace 200 m; 74.2% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.9:1; minor axis 2.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-040 · component 352 (near_trace; 886 closed / 637 emitted px)
Centroid 40.3775°N, 119.3006°W; PCA axis azimuth 6.5° clockwise from north, elongation 8.6:1, axes 11.4 × 1.3 km. Median distance to mapped trace 224 m; 66.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-041 · component 564 (halo; 879 closed / 469 emitted px)
Centroid 40.2302°N, 119.6975°W; PCA axis azimuth 125.2° clockwise from north, elongation 2.8:1, axes 7.0 × 2.5 km. Median distance to mapped trace 200 m; 79.1% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-042 · component 1217 (halo; 859 closed / 578 emitted px)
Centroid 39.8089°N, 119.3971°W; PCA axis azimuth 166.7° clockwise from north, elongation 2.5:1, axes 6.6 × 2.6 km. Median distance to mapped trace 200 m; 79.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-043 · component 1932 (near_trace; 839 closed / 538 emitted px)
Centroid 38.9951°N, 118.0912°W; PCA axis azimuth 20.1° clockwise from north, elongation 4.1:1, axes 7.5 × 1.8 km. Median distance to mapped trace 283 m; 55.6% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-044 · component 2302 (near_trace; 816 closed / 543 emitted px)
Centroid 38.3826°N, 118.0625°W; PCA axis azimuth 161.4° clockwise from north, elongation 8.7:1, axes 13.0 × 1.5 km. Median distance to mapped trace 224 m; 59.1% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.97 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.99 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-045 · component 511 (near_trace; 808 closed / 617 emitted px)
Centroid 40.2666°N, 119.0158°W; PCA axis azimuth 1.3° clockwise from north, elongation 8.1:1, axes 11.0 × 1.4 km. Median distance to mapped trace 224 m; 64.8% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.98 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.01 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-046 · component 6 (near_trace; 798 closed / 587 emitted px)
Centroid 40.6959°N, 117.6534°W; PCA axis azimuth 152.0° clockwise from north, elongation 4.1:1, axes 8.3 × 2.0 km. Median distance to mapped trace 283 m; 56.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.1:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-047 · component 1404 (halo; 756 closed / 461 emitted px)
Centroid 39.5930°N, 119.6330°W; PCA axis azimuth 170.1° clockwise from north, elongation 1.6:1, axes 4.6 × 2.8 km. Median distance to mapped trace 141 m; 81.1% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-048 · component 2424 (near_trace; 741 closed / 445 emitted px)
Centroid 37.9144°N, 118.3686°W; PCA axis azimuth 48.6° clockwise from north, elongation 2.9:1, axes 7.1 × 2.4 km. Median distance to mapped trace 200 m; 70.3% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-049 · component 1377 (halo; 731 closed / 495 emitted px)
Centroid 39.6411°N, 119.2783°W; PCA axis azimuth 59.1° clockwise from north, elongation 1.5:1, axes 4.4 × 2.9 km. Median distance to mapped trace 200 m; 76.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-050 · component 1563 (near_trace; 718 closed / 486 emitted px)
Centroid 39.4158°N, 118.1047°W; PCA axis azimuth 8.4° clockwise from north, elongation 4.4:1, axes 11.3 × 2.6 km. Median distance to mapped trace 224 m; 62.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.4:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-051 · component 763 (halo; 712 closed / 507 emitted px)
Centroid 40.1174°N, 119.0489°W; PCA axis azimuth 171.0° clockwise from north, elongation 7.6:1, axes 10.6 × 1.4 km. Median distance to mapped trace 200 m; 82.1% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-052 · component 1571 (halo; 703 closed / 326 emitted px)
Centroid 39.4217°N, 119.3013°W; PCA axis azimuth 110.2° clockwise from north, elongation 1.9:1, axes 5.1 × 2.7 km. Median distance to mapped trace 141 m; 90.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 2.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-053 · component 2014 (near_trace; 698 closed / 456 emitted px)
Centroid 38.7939°N, 118.0179°W; PCA axis azimuth 175.4° clockwise from north, elongation 2.9:1, axes 6.1 × 2.1 km. Median distance to mapped trace 200 m; 73.2% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-054 · component 1328 (halo; 693 closed / 463 emitted px)
Centroid 39.7030°N, 119.1486°W; PCA axis azimuth 20.2° clockwise from north, elongation 5.5:1, axes 8.9 × 1.6 km. Median distance to mapped trace 141 m; 87.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-055 · component 274 (halo; 690 closed / 472 emitted px)
Centroid 40.4654°N, 117.4353°W; PCA axis azimuth 5.0° clockwise from north, elongation 6.0:1, axes 7.7 × 1.3 km. Median distance to mapped trace 200 m; 87.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-056 · component 1907 (near_trace; 682 closed / 335 emitted px)
Centroid 39.0281°N, 118.8935°W; PCA axis azimuth 164.5° clockwise from north, elongation 2.9:1, axes 8.3 × 2.8 km. Median distance to mapped trace 200 m; 74.6% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-057 · component 2550 (near_trace; 668 closed / 413 emitted px)
Centroid 37.6541°N, 117.5940°W; PCA axis azimuth 30.3° clockwise from north, elongation 2.6:1, axes 6.0 × 2.3 km. Median distance to mapped trace 224 m; 61.0% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 2.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-058 · component 1271 (near_trace; 667 closed / 544 emitted px)
Centroid 39.7557°N, 118.2572°W; PCA axis azimuth 26.2° clockwise from north, elongation 15.9:1, axes 15.9 × 1.0 km. Median distance to mapped trace 539 m; 22.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-059 · component 213 (near_trace; 643 closed / 417 emitted px)
Centroid 40.5311°N, 118.1063°W; PCA axis azimuth 11.8° clockwise from north, elongation 2.5:1, axes 6.0 × 2.4 km. Median distance to mapped trace 300 m; 52.5% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.96 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.08 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-060 · component 1539 (halo; 634 closed / 384 emitted px)
Centroid 39.4416°N, 118.5305°W; PCA axis azimuth 9.3° clockwise from north, elongation 7.2:1, axes 10.9 × 1.5 km. Median distance to mapped trace 141 m; 87.2% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-061 · component 2561 (near_trace; 612 closed / 378 emitted px)
Centroid 37.6139°N, 117.5189°W; PCA axis azimuth 11.8° clockwise from north, elongation 4.5:1, axes 7.2 × 1.6 km. Median distance to mapped trace 308 m; 50.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-062 · component 351 (halo; 608 closed / 322 emitted px)
Centroid 40.3946°N, 119.3907°W; PCA axis azimuth 176.5° clockwise from north, elongation 3.0:1, axes 5.8 × 1.9 km. Median distance to mapped trace 200 m; 78.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (3.0:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-063 · component 2443 (halo; 599 closed / 403 emitted px)
Centroid 37.8466°N, 117.4717°W; PCA axis azimuth 10.1° clockwise from north, elongation 6.3:1, axes 12.2 × 1.9 km. Median distance to mapped trace 141 m; 86.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-064 · component 2505 (halo; 593 closed / 390 emitted px)
Centroid 37.6987°N, 117.4980°W; PCA axis azimuth 17.4° clockwise from north, elongation 7.3:1, axes 14.0 × 1.9 km. Median distance to mapped trace 141 m; 91.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-065 · component 2346 (halo; 592 closed / 368 emitted px)
Centroid 38.1152°N, 117.4780°W; PCA axis azimuth 18.6° clockwise from north, elongation 3.5:1, axes 6.5 × 1.8 km. Median distance to mapped trace 100 m; 94.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-066 · component 1969 (halo; 580 closed / 336 emitted px)
Centroid 38.8723°N, 117.9141°W; PCA axis azimuth 17.4° clockwise from north, elongation 5.9:1, axes 9.0 × 1.5 km. Median distance to mapped trace 200 m; 85.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-067 · component 1952 (halo; 575 closed / 400 emitted px)
Centroid 38.9238°N, 118.1051°W; PCA axis azimuth 24.1° clockwise from north, elongation 4.9:1, axes 6.4 × 1.3 km. Median distance to mapped trace 141 m; 88.2% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.97 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-068 · component 1652 (halo; 574 closed / 379 emitted px)
Centroid 39.3465°N, 118.5702°W; PCA axis azimuth 15.5° clockwise from north, elongation 3.6:1, axes 9.2 × 2.5 km. Median distance to mapped trace 141 m; 88.7% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (3.6:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-069 · component 1743 (halo; 570 closed / 411 emitted px)
Centroid 39.2736°N, 118.4920°W; PCA axis azimuth 85.9° clockwise from north, elongation 1.9:1, axes 4.0 × 2.1 km. Median distance to mapped trace 200 m; 83.2% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-070 · component 510 (halo; 563 closed / 414 emitted px)
Centroid 40.2734°N, 117.6363°W; PCA axis azimuth 10.6° clockwise from north, elongation 11.1:1, axes 13.5 × 1.2 km. Median distance to mapped trace 141 m; 90.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-071 · component 789 (near_trace; 563 closed / 356 emitted px)
Centroid 40.1496°N, 116.1617°W; PCA axis azimuth 10.2° clockwise from north, elongation 1.9:1, axes 3.8 × 2.0 km. Median distance to mapped trace 200 m; 70.5% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.99 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.00 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-072 · component 1862 (halo; 562 closed / 355 emitted px)
Centroid 39.1186°N, 118.1753°W; PCA axis azimuth 35.3° clockwise from north, elongation 4.0:1, axes 7.5 × 1.9 km. Median distance to mapped trace 141 m; 91.8% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-073 · component 228 (near_trace; 557 closed / 394 emitted px)
Centroid 40.4953°N, 118.9695°W; PCA axis azimuth 16.0° clockwise from north, elongation 5.6:1, axes 8.1 × 1.4 km. Median distance to mapped trace 283 m; 59.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 1.00 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-074 · component 2231 (near_trace; 544 closed / 263 emitted px)
Centroid 38.4677°N, 118.3721°W; PCA axis azimuth 15.1° clockwise from north, elongation 1.9:1, axes 5.3 × 2.8 km. Median distance to mapped trace 300 m; 54.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 1.00 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.98 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-075 · component 9 (halo; 529 closed / 364 emitted px)
Centroid 40.7057°N, 116.8722°W; PCA axis azimuth 149.0° clockwise from north, elongation 5.2:1, axes 6.2 × 1.2 km. Median distance to mapped trace 141 m; 86.0% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-076 · component 1110 (halo; 528 closed / 393 emitted px)
Centroid 39.9380°N, 117.9457°W; PCA axis azimuth 56.0° clockwise from north, elongation 7.9:1, axes 16.1 × 2.0 km. Median distance to mapped trace 141 m; 87.0% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (7.9:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-077 · component 371 (halo; 514 closed / 397 emitted px)
Centroid 40.3845°N, 117.5891°W; PCA axis azimuth 17.2° clockwise from north, elongation 6.7:1, axes 8.6 × 1.3 km. Median distance to mapped trace 200 m; 78.1% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-078 · component 404 (near_trace; 508 closed / 360 emitted px)
Centroid 40.3604°N, 118.2437°W; PCA axis azimuth 171.6° clockwise from north, elongation 4.5:1, axes 6.8 × 1.5 km. Median distance to mapped trace 224 m; 58.3% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.05 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-079 · component 1956 (halo; 503 closed / 345 emitted px)
Centroid 38.8987°N, 118.8116°W; PCA axis azimuth 157.1° clockwise from north, elongation 8.1:1, axes 11.8 × 1.5 km. Median distance to mapped trace 141 m; 89.0% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.91 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.94 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-080 · component 2524 (halo; 502 closed / 272 emitted px)
Centroid 37.6957°N, 117.5592°W; PCA axis azimuth 32.1° clockwise from north, elongation 2.7:1, axes 5.9 × 2.2 km. Median distance to mapped trace 200 m; 75.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-081 · component 1115 (near_trace; 491 closed / 397 emitted px)
Centroid 39.9149°N, 118.6380°W; PCA axis azimuth 51.0° clockwise from north, elongation 10.4:1, axes 12.1 × 1.2 km. Median distance to mapped trace 283 m; 57.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-082 · component 334 (near_trace; 488 closed / 399 emitted px)
Centroid 40.4346°N, 116.9245°W; PCA axis azimuth 44.2° clockwise from north, elongation 5.0:1, axes 10.1 × 2.0 km. Median distance to mapped trace 224 m; 67.2% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.0:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-083 · component 2381 (halo; 488 closed / 312 emitted px)
Centroid 38.0047°N, 118.0923°W; PCA axis azimuth 90.9° clockwise from north, elongation 3.7:1, axes 5.7 × 1.6 km. Median distance to mapped trace 100 m; 90.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-084 · component 172 (halo; 487 closed / 331 emitted px)
Centroid 40.5741°N, 117.4891°W; PCA axis azimuth 0.7° clockwise from north, elongation 4.4:1, axes 6.2 × 1.4 km. Median distance to mapped trace 141 m; 94.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-085 · component 726 (halo; 480 closed / 350 emitted px)
Centroid 40.1532°N, 117.8454°W; PCA axis azimuth 17.9° clockwise from north, elongation 12.0:1, axes 10.9 × 0.9 km. Median distance to mapped trace 200 m; 86.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-086 · component 1111 (halo; 476 closed / 291 emitted px)
Centroid 39.9372°N, 118.9979°W; PCA axis azimuth 26.7° clockwise from north, elongation 2.0:1, axes 3.7 × 1.9 km. Median distance to mapped trace 100 m; 90.7% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-087 · component 1290 (near_trace; 475 closed / 217 emitted px)
Centroid 39.7645°N, 118.8726°W; PCA axis azimuth 52.8° clockwise from north, elongation 4.0:1, axes 8.0 × 2.0 km. Median distance to mapped trace 200 m; 67.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-088 · component 141 (halo; 470 closed / 263 emitted px)
Centroid 40.6092°N, 117.2423°W; PCA axis azimuth 2.8° clockwise from north, elongation 2.0:1, axes 5.0 × 2.5 km. Median distance to mapped trace 200 m; 87.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-089 · component 87 (near_trace; 462 closed / 303 emitted px)
Centroid 40.6256°N, 119.1412°W; PCA axis azimuth 19.8° clockwise from north, elongation 3.3:1, axes 6.5 × 2.0 km. Median distance to mapped trace 224 m; 62.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-090 · component 1874 (near_trace; 454 closed / 246 emitted px)
Centroid 39.0971°N, 118.4097°W; PCA axis azimuth 28.0° clockwise from north, elongation 2.4:1, axes 5.9 × 2.5 km. Median distance to mapped trace 300 m; 57.3% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-091 · component 1039 (halo; 447 closed / 253 emitted px)
Centroid 40.0447°N, 117.6225°W; PCA axis azimuth 41.8° clockwise from north, elongation 2.4:1, axes 4.0 × 1.7 km. Median distance to mapped trace 141 m; 89.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-092 · component 954 (halo; 442 closed / 274 emitted px)
Centroid 40.0525°N, 117.8113°W; PCA axis azimuth 22.6° clockwise from north, elongation 9.1:1, axes 8.3 × 0.9 km. Median distance to mapped trace 141 m; 87.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-093 · component 1938 (halo; 441 closed / 337 emitted px)
Centroid 38.9764°N, 118.1614°W; PCA axis azimuth 4.4° clockwise from north, elongation 7.0:1, axes 7.8 × 1.1 km. Median distance to mapped trace 200 m; 81.9% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-094 · component 1557 (near_trace; 436 closed / 332 emitted px)
Centroid 39.4435°N, 118.2156°W; PCA axis azimuth 12.8° clockwise from north, elongation 2.8:1, axes 4.3 × 1.6 km. Median distance to mapped trace 500 m; 33.4% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-095 · component 2581 (near_trace; 435 closed / 244 emitted px)
Centroid 37.4202°N, 117.8126°W; PCA axis azimuth 141.4° clockwise from north, elongation 1.8:1, axes 3.9 × 2.1 km. Median distance to mapped trace 224 m; 61.5% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-096 · component 1400 (halo; 433 closed / 223 emitted px)
Centroid 39.5959°N, 119.6658°W; PCA axis azimuth 2.2° clockwise from north, elongation 2.5:1, axes 5.3 × 2.1 km. Median distance to mapped trace 100 m; 87.4% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-097 · component 784 (near_trace; 428 closed / 314 emitted px)
Centroid 40.1355°N, 117.0634°W; PCA axis azimuth 25.8° clockwise from north, elongation 4.8:1, axes 8.6 × 1.8 km. Median distance to mapped trace 224 m; 58.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-098 · component 835 (near_trace; 428 closed / 294 emitted px)
Centroid 40.0912°N, 119.2944°W; PCA axis azimuth 171.1° clockwise from north, elongation 5.5:1, axes 7.2 × 1.3 km. Median distance to mapped trace 200 m; 70.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-099 · component 1717 (near_trace; 427 closed / 323 emitted px)
Centroid 39.3051°N, 118.8684°W; PCA axis azimuth 133.3° clockwise from north, elongation 4.0:1, axes 5.0 × 1.3 km. Median distance to mapped trace 200 m; 71.2% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.94 regional percentile of the component median), magnetic gradient/contact (mag_hgm, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-100 · component 1854 (near_trace; 421 closed / 236 emitted px)
Centroid 39.1280°N, 118.2321°W; PCA axis azimuth 154.5° clockwise from north, elongation 2.6:1, axes 5.6 × 2.2 km. Median distance to mapped trace 200 m; 61.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-101 · component 1024 (halo; 418 closed / 309 emitted px)
Centroid 40.0084°N, 119.2905°W; PCA axis azimuth 161.7° clockwise from north, elongation 7.0:1, axes 10.0 × 1.4 km. Median distance to mapped trace 141 m; 90.3% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-102 · component 348 (halo; 413 closed / 237 emitted px)
Centroid 40.4250°N, 118.6869°W; PCA axis azimuth 50.3° clockwise from north, elongation 1.9:1, axes 3.5 × 1.8 km. Median distance to mapped trace 141 m; 76.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-103 · component 1853 (halo; 406 closed / 289 emitted px)
Centroid 39.1198°N, 118.3210°W; PCA axis azimuth 179.3° clockwise from north, elongation 5.1:1, axes 9.0 × 1.8 km. Median distance to mapped trace 141 m; 83.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.95 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-104 · component 323 (halo; 400 closed / 304 emitted px)
Centroid 40.4215°N, 116.2727°W; PCA axis azimuth 10.7° clockwise from north, elongation 10.4:1, axes 9.5 × 0.9 km. Median distance to mapped trace 171 m; 88.2% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.06 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-105 · component 1327 (near_trace; 394 closed / 234 emitted px)
Centroid 39.7032°N, 119.5824°W; PCA axis azimuth 154.9° clockwise from north, elongation 2.3:1, axes 5.5 × 2.4 km. Median distance to mapped trace 200 m; 71.8% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-106 · component 177 (halo; 390 closed / 257 emitted px)
Centroid 40.5747°N, 117.9700°W; PCA axis azimuth 27.9° clockwise from north, elongation 3.6:1, axes 4.7 × 1.3 km. Median distance to mapped trace 141 m; 89.1% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.09 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-107 · component 681 (near_trace; 373 closed / 194 emitted px)
Centroid 40.2030°N, 117.6709°W; PCA axis azimuth 24.8° clockwise from north, elongation 1.2:1, axes 2.8 × 2.4 km. Median distance to mapped trace 141 m; 71.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.2:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-108 · component 1574 (near_trace; 372 closed / 216 emitted px)
Centroid 39.4243°N, 119.2608°W; PCA axis azimuth 149.9° clockwise from north, elongation 1.3:1, axes 2.6 × 2.0 km. Median distance to mapped trace 224 m; 69.0% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 1.00 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-109 · component 1472 (near_trace; 354 closed / 240 emitted px)
Centroid 39.5420°N, 117.9939°W; PCA axis azimuth 139.7° clockwise from north, elongation 2.7:1, axes 4.5 × 1.6 km. Median distance to mapped trace 291 m; 57.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-110 · component 2201 (halo; 354 closed / 198 emitted px)
Centroid 38.5194°N, 118.4178°W; PCA axis azimuth 132.1° clockwise from north, elongation 1.9:1, axes 3.5 × 1.9 km. Median distance to mapped trace 141 m; 87.9% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.99 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-111 · component 1201 (halo; 353 closed / 244 emitted px)
Centroid 39.8372°N, 118.2166°W; PCA axis azimuth 1.0° clockwise from north, elongation 5.0:1, axes 7.0 × 1.4 km. Median distance to mapped trace 200 m; 81.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-112 · component 1635 (halo; 350 closed / 242 emitted px)
Centroid 39.3638°N, 117.9762°W; PCA axis azimuth 15.3° clockwise from north, elongation 14.6:1, axes 11.8 × 0.8 km. Median distance to mapped trace 100 m; 98.8% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-113 · component 1846 (halo; 350 closed / 218 emitted px)
Centroid 39.1412°N, 118.0831°W; PCA axis azimuth 86.6° clockwise from north, elongation 1.2:1, axes 4.5 × 3.6 km. Median distance to mapped trace 141 m; 92.2% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.98 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.90 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.2:1; minor axis 3.6 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-114 · component 410 (halo; 346 closed / 240 emitted px)
Centroid 40.3360°N, 119.6405°W; PCA axis azimuth 171.5° clockwise from north, elongation 4.8:1, axes 5.8 × 1.2 km. Median distance to mapped trace 200 m; 76.7% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-115 · component 126 (halo; 341 closed / 275 emitted px)
Centroid 40.6272°N, 117.9353°W; PCA axis azimuth 48.7° clockwise from north, elongation 7.9:1, axes 6.8 × 0.9 km. Median distance to mapped trace 200 m; 83.6% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.04 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-116 · component 2139 (halo; 335 closed / 218 emitted px)
Centroid 38.5961°N, 118.3309°W; PCA axis azimuth 142.9° clockwise from north, elongation 8.2:1, axes 8.6 × 1.1 km. Median distance to mapped trace 141 m; 83.5% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.91 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.97 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-117 · component 367 (halo; 331 closed / 229 emitted px)
Centroid 40.3770°N, 118.8235°W; PCA axis azimuth 11.6° clockwise from north, elongation 6.3:1, axes 7.9 × 1.2 km. Median distance to mapped trace 200 m; 81.7% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.09 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-118 · component 377 (halo; 327 closed / 227 emitted px)
Centroid 40.3778°N, 119.0438°W; PCA axis azimuth 42.6° clockwise from north, elongation 6.5:1, axes 7.1 × 1.1 km. Median distance to mapped trace 200 m; 77.5% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 1.00 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-119 · component 419 (near_trace; 323 closed / 251 emitted px)
Centroid 40.3697°N, 116.3475°W; PCA axis azimuth 52.9° clockwise from north, elongation 3.6:1, axes 4.8 × 1.3 km. Median distance to mapped trace 224 m; 66.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-120 · component 2130 (halo; 323 closed / 176 emitted px)
Centroid 38.6236°N, 118.2074°W; PCA axis azimuth 134.0° clockwise from north, elongation 4.9:1, axes 5.7 × 1.2 km. Median distance to mapped trace 141 m; 92.6% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.97 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-121 · component 10 (halo; 319 closed / 215 emitted px)
Centroid 40.7091°N, 116.7514°W; PCA axis azimuth 55.0° clockwise from north, elongation 4.0:1, axes 6.6 × 1.7 km. Median distance to mapped trace 141 m; 91.6% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-122 · component 958 (near_trace; 314 closed / 204 emitted px)
Centroid 40.0671°N, 117.0106°W; PCA axis azimuth 18.1° clockwise from north, elongation 5.6:1, axes 6.2 × 1.1 km. Median distance to mapped trace 316 m; 48.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-123 · component 2191 (near_trace; 310 closed / 147 emitted px)
Centroid 38.5382°N, 117.8858°W; PCA axis azimuth 45.2° clockwise from north, elongation 1.7:1, axes 3.2 × 1.9 km. Median distance to mapped trace 316 m; 49.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-124 · component 599 (halo; 304 closed / 232 emitted px)
Centroid 40.2270°N, 118.1613°W; PCA axis azimuth 23.7° clockwise from north, elongation 8.1:1, axes 7.9 × 1.0 km. Median distance to mapped trace 141 m; 87.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-125 · component 940 (near_trace; 301 closed / 188 emitted px)
Centroid 40.0841°N, 117.0938°W; PCA axis azimuth 11.8° clockwise from north, elongation 1.8:1, axes 3.0 × 1.6 km. Median distance to mapped trace 412 m; 42.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-126 · component 1089 (halo; 300 closed / 178 emitted px)
Centroid 39.9882°N, 119.0181°W; PCA axis azimuth 14.0° clockwise from north, elongation 2.1:1, axes 3.1 × 1.5 km. Median distance to mapped trace 200 m; 84.8% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-127 · component 1529 (near_trace; 300 closed / 209 emitted px)
Centroid 39.4685°N, 119.1646°W; PCA axis azimuth 140.8° clockwise from north, elongation 2.5:1, axes 4.4 × 1.8 km. Median distance to mapped trace 224 m; 56.9% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-128 · component 669 (halo; 298 closed / 219 emitted px)
Centroid 40.2013°N, 117.4653°W; PCA axis azimuth 16.6° clockwise from north, elongation 7.7:1, axes 7.1 × 0.9 km. Median distance to mapped trace 141 m; 93.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-129 · component 258 (halo; 295 closed / 222 emitted px)
Centroid 40.5029°N, 116.7852°W; PCA axis azimuth 60.9° clockwise from north, elongation 4.8:1, axes 5.1 × 1.1 km. Median distance to mapped trace 141 m; 93.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-130 · component 906 (near_trace; 295 closed / 253 emitted px)
Centroid 40.0856°N, 117.5454°W; PCA axis azimuth 29.8° clockwise from north, elongation 9.2:1, axes 7.3 × 0.8 km. Median distance to mapped trace 224 m; 63.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-131 · component 1556 (halo; 295 closed / 172 emitted px)
Centroid 39.4457°N, 119.1278°W; PCA axis azimuth 99.3° clockwise from north, elongation 1.4:1, axes 2.6 × 1.9 km. Median distance to mapped trace 200 m; 83.7% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-132 · component 1341 (halo; 293 closed / 130 emitted px)
Centroid 39.7085°N, 118.9913°W; PCA axis azimuth 73.4° clockwise from north, elongation 2.0:1, axes 3.8 × 1.9 km. Median distance to mapped trace 141 m; 90.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-133 · component 1170 (halo; 290 closed / 209 emitted px)
Centroid 39.8831°N, 119.1542°W; PCA axis azimuth 21.1° clockwise from north, elongation 1.8:1, axes 2.6 × 1.5 km. Median distance to mapped trace 141 m; 94.3% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-134 · component 521 (near_trace; 287 closed / 133 emitted px)
Centroid 40.2765°N, 119.0666°W; PCA axis azimuth 25.6° clockwise from north, elongation 5.8:1, axes 5.7 × 1.0 km. Median distance to mapped trace 224 m; 63.9% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.03 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-135 · component 667 (near_trace; 283 closed / 204 emitted px)
Centroid 40.2039°N, 118.3794°W; PCA axis azimuth 35.8° clockwise from north, elongation 3.5:1, axes 4.5 × 1.3 km. Median distance to mapped trace 224 m; 69.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-136 · component 730 (halo; 282 closed / 209 emitted px)
Centroid 40.1756°N, 116.6535°W; PCA axis azimuth 50.4° clockwise from north, elongation 5.6:1, axes 9.4 × 1.7 km. Median distance to mapped trace 141 m; 93.8% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.01 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-137 · component 1607 (halo; 281 closed / 157 emitted px)
Centroid 39.3898°N, 119.3200°W; PCA axis azimuth 24.6° clockwise from north, elongation 3.5:1, axes 3.9 × 1.1 km. Median distance to mapped trace 141 m; 79.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-138 · component 273 (near_trace; 279 closed / 209 emitted px)
Centroid 40.4904°N, 116.8442°W; PCA axis azimuth 51.5° clockwise from north, elongation 2.7:1, axes 4.0 × 1.5 km. Median distance to mapped trace 200 m; 74.2% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-139 · component 618 (halo; 271 closed / 169 emitted px)
Centroid 40.2151°N, 119.4467°W; PCA axis azimuth 4.0° clockwise from north, elongation 1.9:1, axes 2.9 × 1.5 km. Median distance to mapped trace 141 m; 81.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-140 · component 1349 (halo; 271 closed / 163 emitted px)
Centroid 39.6860°N, 119.1923°W; PCA axis azimuth 38.2° clockwise from north, elongation 1.1:1, axes 2.1 × 1.9 km. Median distance to mapped trace 141 m; 77.3% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-141 · component 119 (near_trace; 270 closed / 165 emitted px)
Centroid 40.6470°N, 117.2271°W; PCA axis azimuth 72.2° clockwise from north, elongation 1.4:1, axes 3.3 × 2.3 km. Median distance to mapped trace 283 m; 58.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 2.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-142 · component 689 (halo; 269 closed / 182 emitted px)
Centroid 40.1597°N, 119.5081°W; PCA axis azimuth 173.7° clockwise from north, elongation 9.9:1, axes 6.8 × 0.7 km. Median distance to mapped trace 100 m; 96.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-143 · component 1222 (near_trace; 268 closed / 159 emitted px)
Centroid 39.8157°N, 119.7432°W; PCA axis azimuth 125.8° clockwise from north, elongation 4.3:1, axes 5.0 × 1.2 km. Median distance to mapped trace 224 m; 64.2% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-144 · component 1919 (halo; 268 closed / 166 emitted px)
Centroid 39.0369°N, 118.1450°W; PCA axis azimuth 44.5° clockwise from north, elongation 1.9:1, axes 3.6 × 1.9 km. Median distance to mapped trace 200 m; 86.1% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.91 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-145 · component 223 (near_trace; 267 closed / 178 emitted px)
Centroid 40.5306°N, 117.5608°W; PCA axis azimuth 164.0° clockwise from north, elongation 6.1:1, axes 5.6 × 0.9 km. Median distance to mapped trace 200 m; 64.6% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-146 · component 1284 (halo; 266 closed / 172 emitted px)
Centroid 39.7602°N, 119.3569°W; PCA axis azimuth 148.2° clockwise from north, elongation 2.1:1, axes 3.0 × 1.4 km. Median distance to mapped trace 141 m; 95.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-147 · component 395 (halo; 265 closed / 186 emitted px)
Centroid 40.3531°N, 119.2621°W; PCA axis azimuth 14.7° clockwise from north, elongation 8.7:1, axes 6.3 × 0.7 km. Median distance to mapped trace 200 m; 82.3% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-148 · component 200 (near_trace; 259 closed / 184 emitted px)
Centroid 40.5253°N, 119.5960°W; PCA axis azimuth 39.9° clockwise from north, elongation 8.3:1, axes 6.8 × 0.8 km. Median distance to mapped trace 224 m; 73.4% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-149 · component 221 (halo; 252 closed / 154 emitted px)
Centroid 40.5147°N, 118.9984°W; PCA axis azimuth 9.0° clockwise from north, elongation 4.6:1, axes 5.7 × 1.2 km. Median distance to mapped trace 141 m; 92.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-150 · component 2502 (halo; 252 closed / 176 emitted px)
Centroid 37.7334°N, 117.3711°W; PCA axis azimuth 6.1° clockwise from north, elongation 4.6:1, axes 4.4 × 0.9 km. Median distance to mapped trace 141 m; 75.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-151 · component 406 (near_trace; 248 closed / 146 emitted px)
Centroid 40.3743°N, 116.9776°W; PCA axis azimuth 25.0° clockwise from north, elongation 2.4:1, axes 3.1 × 1.3 km. Median distance to mapped trace 283 m; 60.3% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-152 · component 205 (halo; 247 closed / 184 emitted px)
Centroid 40.5483°N, 117.4181°W; PCA axis azimuth 28.8° clockwise from north, elongation 8.8:1, axes 6.1 × 0.7 km. Median distance to mapped trace 141 m; 92.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-153 · component 878 (near_trace; 243 closed / 140 emitted px)
Centroid 40.1076°N, 116.9331°W; PCA axis azimuth 25.2° clockwise from north, elongation 6.8:1, axes 6.8 × 1.0 km. Median distance to mapped trace 141 m; 73.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-154 · component 910 (near_trace; 242 closed / 154 emitted px)
Centroid 40.0976°N, 116.8721°W; PCA axis azimuth 50.4° clockwise from north, elongation 5.2:1, axes 7.2 × 1.4 km. Median distance to mapped trace 200 m; 61.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-155 · component 1597 (halo; 242 closed / 161 emitted px)
Centroid 39.4154°N, 117.9375°W; PCA axis azimuth 177.9° clockwise from north, elongation 4.2:1, axes 4.7 × 1.1 km. Median distance to mapped trace 200 m; 85.1% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-156 · component 2533 (halo; 241 closed / 175 emitted px)
Centroid 37.6831°N, 117.9674°W; PCA axis azimuth 11.6° clockwise from north, elongation 3.2:1, axes 5.2 × 1.6 km. Median distance to mapped trace 200 m; 76.0% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-157 · component 139 (near_trace; 239 closed / 177 emitted px)
Centroid 40.6184°N, 118.1160°W; PCA axis azimuth 60.1° clockwise from north, elongation 4.5:1, axes 5.6 × 1.2 km. Median distance to mapped trace 316 m; 48.0% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.91 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.06 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-158 · component 316 (halo; 239 closed / 142 emitted px)
Centroid 40.4392°N, 118.1072°W; PCA axis azimuth 2.5° clockwise from north, elongation 4.0:1, axes 4.3 × 1.1 km. Median distance to mapped trace 141 m; 86.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-159 · component 744 (near_trace; 238 closed / 219 emitted px)
Centroid 40.1532°N, 119.2096°W; PCA axis azimuth 25.6° clockwise from north, elongation 6.6:1, axes 4.8 × 0.7 km. Median distance to mapped trace 300 m; 57.1% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-160 · component 445 (near_trace; 237 closed / 197 emitted px)
Centroid 40.3291°N, 118.9988°W; PCA axis azimuth 19.8° clockwise from north, elongation 5.1:1, axes 4.2 × 0.8 km. Median distance to mapped trace 985 m; 18.3% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-161 · component 711 (halo; 235 closed / 119 emitted px)
Centroid 40.1885°N, 118.3122°W; PCA axis azimuth 32.5° clockwise from north, elongation 1.9:1, axes 2.9 × 1.6 km. Median distance to mapped trace 141 m; 89.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-162 · component 399 (near_trace; 230 closed / 164 emitted px)
Centroid 40.3594°N, 118.8560°W; PCA axis azimuth 3.0° clockwise from north, elongation 4.8:1, axes 4.2 × 0.9 km. Median distance to mapped trace 200 m; 68.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.99 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.05 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-163 · component 1699 (near_trace; 224 closed / 161 emitted px)
Centroid 39.3318°N, 118.1278°W; PCA axis azimuth 28.1° clockwise from north, elongation 3.3:1, axes 3.5 × 1.1 km. Median distance to mapped trace 412 m; 44.7% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-164 · component 463 (halo; 223 closed / 138 emitted px)
Centroid 40.3345°N, 118.7176°W; PCA axis azimuth 67.8° clockwise from north, elongation 1.8:1, axes 2.5 × 1.4 km. Median distance to mapped trace 141 m; 89.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-165 · component 282 (near_trace; 218 closed / 137 emitted px)
Centroid 40.4823°N, 116.8773°W; PCA axis azimuth 31.2° clockwise from north, elongation 1.8:1, axes 2.6 × 1.4 km. Median distance to mapped trace 224 m; 69.3% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-166 · component 532 (halo; 217 closed / 139 emitted px)
Centroid 40.2623°N, 119.4307°W; PCA axis azimuth 15.0° clockwise from north, elongation 8.8:1, axes 6.7 × 0.8 km. Median distance to mapped trace 141 m; 85.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-167 · component 167 (halo; 213 closed / 142 emitted px)
Centroid 40.5662°N, 119.0873°W; PCA axis azimuth 7.0° clockwise from north, elongation 4.6:1, axes 6.0 × 1.3 km. Median distance to mapped trace 200 m; 77.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-168 · component 2545 (halo; 209 closed / 98 emitted px)
Centroid 37.6645°N, 117.4728°W; PCA axis azimuth 16.2° clockwise from north, elongation 4.5:1, axes 4.4 × 1.0 km. Median distance to mapped trace 100 m; 96.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-169 · component 271 (halo; 208 closed / 145 emitted px)
Centroid 40.4740°N, 118.0547°W; PCA axis azimuth 0.1° clockwise from north, elongation 8.7:1, axes 5.4 × 0.6 km. Median distance to mapped trace 141 m; 91.0% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-170 · component 1363 (near_trace; 208 closed / 120 emitted px)
Centroid 39.6652°N, 119.2896°W; PCA axis azimuth 32.7° clockwise from north, elongation 2.4:1, axes 3.7 × 1.5 km. Median distance to mapped trace 212 m; 71.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-171 · component 2016 (near_trace; 208 closed / 126 emitted px)
Centroid 38.7971°N, 117.8429°W; PCA axis azimuth 165.2° clockwise from north, elongation 9.3:1, axes 6.6 × 0.7 km. Median distance to mapped trace 141 m; 74.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-172 · component 728 (isolated; 207 closed / 143 emitted px)
Centroid 40.1860°N, 117.0411°W; PCA axis azimuth 7.2° clockwise from north, elongation 3.4:1, axes 3.3 × 1.0 km. Median distance to mapped trace 721 m; 9.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-173 · component 2488 (near_trace; 207 closed / 153 emitted px)
Centroid 37.7677°N, 117.9821°W; PCA axis azimuth 66.1° clockwise from north, elongation 2.5:1, axes 3.0 × 1.2 km. Median distance to mapped trace 283 m; 52.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-174 · component 1155 (near_trace; 206 closed / 136 emitted px)
Centroid 39.8926°N, 119.0773°W; PCA axis azimuth 0.5° clockwise from north, elongation 2.9:1, axes 2.8 × 1.0 km. Median distance to mapped trace 253 m; 66.2% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 1.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-175 · component 1484 (near_trace; 206 closed / 101 emitted px)
Centroid 39.5111°N, 119.2438°W; PCA axis azimuth 127.7° clockwise from north, elongation 2.5:1, axes 3.2 × 1.3 km. Median distance to mapped trace 316 m; 48.5% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-176 · component 1798 (near_trace; 206 closed / 177 emitted px)
Centroid 39.2027°N, 118.4002°W; PCA axis azimuth 24.5° clockwise from north, elongation 8.1:1, axes 5.7 × 0.7 km. Median distance to mapped trace 283 m; 60.5% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.93 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-177 · component 5 (halo; 204 closed / 151 emitted px)
Centroid 40.6893°N, 118.8959°W; PCA axis azimuth 22.0° clockwise from north, elongation 5.0:1, axes 4.8 × 1.0 km. Median distance to mapped trace 141 m; 80.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-178 · component 1094 (near_trace; 204 closed / 159 emitted px)
Centroid 39.9945°N, 117.8551°W; PCA axis azimuth 37.8° clockwise from north, elongation 9.3:1, axes 6.4 × 0.7 km. Median distance to mapped trace 200 m; 69.2% within 300 m.
**Measured support:** slope break on the 100 m detrended elevation (slope_of_slope, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-179 · component 457 (halo; 202 closed / 108 emitted px)
Centroid 40.3453°N, 116.5090°W; PCA axis azimuth 3.4° clockwise from north, elongation 1.6:1, axes 3.1 × 1.9 km. Median distance to mapped trace 141 m; 95.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-180 · component 1998 (halo; 201 closed / 129 emitted px)
Centroid 38.8335°N, 118.7777°W; PCA axis azimuth 164.4° clockwise from north, elongation 4.1:1, axes 3.8 × 0.9 km. Median distance to mapped trace 200 m; 90.7% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.
