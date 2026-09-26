# Geological hypotheses for the current model's flagged components

**Raster:** `gems6_experiment_drop2_topk05_w3.tif`; SHA-256 `1f551a93c6764acfe75bead7fdf9d1432c251e5dd4edde2b9fefc97c672d8cda`. This is a pixel prediction, **not an expert-verified fault map or a leaderboard result**.
**Method:** 5×5-pixel morphological closing of 630,621 off-catalogue positive pixels produced 957 components. The 343 at ≥200 closed pixels are reviewed below, **all 343** (not just the top ten). The remaining 614 smaller components have not been geologically interpreted and must not be called discovered faults. All are accounted for in the [fragment inventory](local_candidate_w3_geology_fragments_2026-09-26.csv) (41,755 emitted px, each assessed 'not an identified fault by this screen'). A further 508 off-catalogue emitted px were not retained by closing and were not assigned to a component (the grid boundary can cause this).
Class is a **distance heuristic**, not a geological label: 54 isolated, 274 near a mapped trace, 15 mapped-trace halos. The closed component defines groups/PCA and can contain non-predicted bridging pixels; band summaries and mapped-trace distances use **emitted, off-catalogue pixels** only.

Signals are medians over emitted pixels expressed as regional percentiles of all-band-valid locations on the pinned 100 m feature raster ([official band descriptions](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features)); 90th/10th-percentile thresholds are descriptive, not validated likelihoods. Magnetic gradients and gravity gradients may be lithological contacts; slope breaks may be erosional; strain and earthquake layers may describe broad zones; conductivity can reflect lithology as well as fluids. The supplied magnetic tilt is not calibrated to derive depth and is excluded from agreement. None of the six families is asserted to be statistically independent of the others.

The [official metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) uses a 300 m kernel, while [DrivenData staff](https://community.drivendata.org/t/11516/4) clarified that the known-fault mask is **pixel-exact**, not buffered: a correction may be within 300 m of a known trace, but a halo with no new fault is penalized. [Staff also declined to disclose test-fault sources, types, or coverage](https://community.drivendata.org/t/11527/7). Do not use this page to assert those unknowns.

The [official study context](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/#about-the-data) mentions the Walker Lane and western Great Basin, but NO individual component is assigned to a specific fault system or regime from PCA orientation alone. PCA strike is an axis, not a verified fault trend. Original 1 m DEM/field observations and a mapped system-level geologist review are required to choose between each hypothesis and its counterexample. **No depth estimates are offered.**

## Assessments (every ≥200 px component)

### S-001 · component 810 (near_trace; 41,322 closed / 35,748 emitted px)
Centroid 38.5224°N, 117.9418°W; PCA axis azimuth 144.6° clockwise from north, elongation 3.1:1, axes 52.7 × 17.0 km. Median distance to mapped trace 361 m; 46.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.1:1; minor axis 17.0 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-002 · component 382 (near_trace; 38,365 closed / 33,688 emitted px)
Centroid 39.5639°N, 118.1618°W; PCA axis azimuth 22.3° clockwise from north, elongation 6.7:1, axes 124.6 × 18.6 km. Median distance to mapped trace 316 m; 47.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (6.7:1; minor axis 18.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-003 · component 885 (near_trace; 22,783 closed / 20,364 emitted px)
Centroid 38.0323°N, 118.4562°W; PCA axis azimuth 98.2° clockwise from north, elongation 3.1:1, axes 31.9 × 10.3 km. Median distance to mapped trace 300 m; 50.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.96 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 1.00 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.1:1; minor axis 10.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-004 · component 927 (near_trace; 20,533 closed / 18,166 emitted px)
Centroid 37.6285°N, 118.0369°W; PCA axis azimuth 147.3° clockwise from north, elongation 8.3:1, axes 80.1 × 9.7 km. Median distance to mapped trace 361 m; 46.2% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (8.3:1; minor axis 9.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-005 · component 623 (near_trace; 17,729 closed / 15,599 emitted px)
Centroid 39.3075°N, 118.1216°W; PCA axis azimuth 13.6° clockwise from north, elongation 3.6:1, axes 46.7 × 13.1 km. Median distance to mapped trace 400 m; 39.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.6:1; minor axis 13.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-006 · component 36 (near_trace; 15,525 closed / 13,701 emitted px)
Centroid 40.5480°N, 116.8134°W; PCA axis azimuth 39.9° clockwise from north, elongation 3.5:1, axes 46.8 × 13.5 km. Median distance to mapped trace 316 m; 47.9% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.5:1; minor axis 13.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-007 · component 302 (near_trace; 14,796 closed / 12,995 emitted px)
Centroid 40.1276°N, 118.7558°W; PCA axis azimuth 13.7° clockwise from north, elongation 2.0:1, axes 25.1 × 12.6 km. Median distance to mapped trace 412 m; 39.5% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.08 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 12.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-008 · component 937 (near_trace; 13,613 closed / 11,884 emitted px)
Centroid 37.6718°N, 117.4592°W; PCA axis azimuth 28.3° clockwise from north, elongation 2.2:1, axes 24.4 × 11.3 km. Median distance to mapped trace 400 m; 39.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 11.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-009 · component 489 (near_trace; 12,719 closed / 10,784 emitted px)
Centroid 39.7189°N, 119.3520°W; PCA axis azimuth 158.2° clockwise from north, elongation 2.6:1, axes 33.2 × 12.8 km. Median distance to mapped trace 361 m; 44.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 12.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-010 · component 110 (near_trace; 11,346 closed / 9,676 emitted px)
Centroid 40.3213°N, 117.6121°W; PCA axis azimuth 15.8° clockwise from north, elongation 6.0:1, axes 58.6 × 9.8 km. Median distance to mapped trace 316 m; 48.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (6.0:1; minor axis 9.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-011 · component 908 (near_trace; 9,121 closed / 7,986 emitted px)
Centroid 37.8430°N, 117.9252°W; PCA axis azimuth 27.4° clockwise from north, elongation 2.8:1, axes 25.7 × 9.3 km. Median distance to mapped trace 300 m; 51.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 9.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-012 · component 151 (near_trace; 9,078 closed / 8,166 emitted px)
Centroid 40.2632°N, 116.4837°W; PCA axis azimuth 42.3° clockwise from north, elongation 5.3:1, axes 64.4 × 12.2 km. Median distance to mapped trace 316 m; 49.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.3:1; minor axis 12.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-013 · component 572 (near_trace; 8,992 closed / 7,582 emitted px)
Centroid 39.4947°N, 119.2061°W; PCA axis azimuth 135.3° clockwise from north, elongation 2.7:1, axes 23.9 × 8.8 km. Median distance to mapped trace 400 m; 43.2% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 8.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-014 · component 626 (near_trace; 8,976 closed / 7,432 emitted px)
Centroid 39.3901°N, 119.3026°W; PCA axis azimuth 30.0° clockwise from north, elongation 1.9:1, axes 21.8 × 11.4 km. Median distance to mapped trace 283 m; 53.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 11.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-015 · component 92 (near_trace; 8,700 closed / 7,486 emitted px)
Centroid 40.4383°N, 117.4445°W; PCA axis azimuth 11.2° clockwise from north, elongation 7.2:1, axes 39.3 × 5.4 km. Median distance to mapped trace 316 m; 49.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (7.2:1; minor axis 5.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-016 · component 66 (near_trace; 8,346 closed / 7,329 emitted px)
Centroid 40.4928°N, 118.2426°W; PCA axis azimuth 6.7° clockwise from north, elongation 5.8:1, axes 38.3 × 6.6 km. Median distance to mapped trace 361 m; 44.3% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.92 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.06 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.8:1; minor axis 6.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-017 · component 201 (near_trace; 8,066 closed / 7,080 emitted px)
Centroid 40.1683°N, 119.0222°W; PCA axis azimuth 3.7° clockwise from north, elongation 8.9:1, axes 55.5 × 6.3 km. Median distance to mapped trace 316 m; 47.9% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (8.9:1; minor axis 6.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-018 · component 733 (near_trace; 7,600 closed / 6,666 emitted px)
Centroid 38.9898°N, 118.8670°W; PCA axis azimuth 157.6° clockwise from north, elongation 6.9:1, axes 38.6 × 5.6 km. Median distance to mapped trace 316 m; 50.0% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.95 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (6.9:1; minor axis 5.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-019 · component 545 (near_trace; 7,551 closed / 6,515 emitted px)
Centroid 39.6600°N, 119.0318°W; PCA axis azimuth 17.5° clockwise from north, elongation 1.9:1, axes 16.1 × 8.4 km. Median distance to mapped trace 539 m; 32.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 8.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-020 · component 880 (near_trace; 7,530 closed / 6,543 emitted px)
Centroid 38.0382°N, 117.5595°W; PCA axis azimuth 42.2° clockwise from north, elongation 4.7:1, axes 29.0 × 6.2 km. Median distance to mapped trace 316 m; 48.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.7:1; minor axis 6.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-021 · component 495 (near_trace; 7,481 closed / 6,759 emitted px)
Centroid 39.8128°N, 118.4592°W; PCA axis azimuth 17.6° clockwise from north, elongation 2.1:1, axes 14.3 × 6.9 km. Median distance to mapped trace 300 m; 50.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 6.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-022 · component 541 (near_trace; 6,952 closed / 5,815 emitted px)
Centroid 39.6329°N, 119.6206°W; PCA axis azimuth 25.7° clockwise from north, elongation 3.7:1, axes 23.6 × 6.4 km. Median distance to mapped trace 300 m; 53.4% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.7:1; minor axis 6.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-023 · component 820 (near_trace; 6,951 closed / 5,949 emitted px)
Centroid 38.6309°N, 118.4395°W; PCA axis azimuth 146.1° clockwise from north, elongation 1.8:1, axes 16.4 × 9.4 km. Median distance to mapped trace 424 m; 36.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.97 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.98 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 9.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-024 · component 843 (near_trace; 6,619 closed / 5,630 emitted px)
Centroid 38.4857°N, 118.3759°W; PCA axis azimuth 97.1° clockwise from north, elongation 1.6:1, axes 16.8 × 10.4 km. Median distance to mapped trace 412 m; 40.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 1.00 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.97 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 10.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-025 · component 754 (near_trace; 6,203 closed / 5,452 emitted px)
Centroid 38.9600°N, 118.0919°W; PCA axis azimuth 10.1° clockwise from north, elongation 3.6:1, axes 20.6 × 5.8 km. Median distance to mapped trace 400 m; 40.9% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.95 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.6:1; minor axis 5.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-026 · component 850 (near_trace; 6,118 closed / 5,359 emitted px)
Centroid 38.3629°N, 118.0451°W; PCA axis azimuth 161.1° clockwise from north, elongation 9.9:1, axes 36.4 × 3.7 km. Median distance to mapped trace 447 m; 34.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (9.9:1; minor axis 3.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-027 · component 148 (near_trace; 5,447 closed / 4,953 emitted px)
Centroid 40.4206°N, 119.1217°W; PCA axis azimuth 14.3° clockwise from north, elongation 2.0:1, axes 12.1 × 6.0 km. Median distance to mapped trace 283 m; 54.7% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 6.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-028 · component 294 (near_trace; 5,201 closed / 4,434 emitted px)
Centroid 40.1525°N, 117.5025°W; PCA axis azimuth 24.4° clockwise from north, elongation 5.4:1, axes 29.3 × 5.4 km. Median distance to mapped trace 424 m; 36.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.4:1; minor axis 5.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-029 · component 240 (near_trace; 5,145 closed / 4,595 emitted px)
Centroid 40.1851°N, 118.3685°W; PCA axis azimuth 20.0° clockwise from north, elongation 6.4:1, axes 40.3 × 6.3 km. Median distance to mapped trace 412 m; 37.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (6.4:1; minor axis 6.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-030 · component 275 (near_trace; 4,934 closed / 4,360 emitted px)
Centroid 40.1184°N, 119.2848°W; PCA axis azimuth 7.2° clockwise from north, elongation 7.5:1, axes 37.0 × 4.9 km. Median distance to mapped trace 316 m; 46.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (7.5:1; minor axis 4.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-031 · component 838 (near_trace; 4,706 closed / 4,259 emitted px)
Centroid 38.4902°N, 118.6546°W; PCA axis azimuth 154.0° clockwise from north, elongation 8.1:1, axes 27.3 × 3.4 km. Median distance to mapped trace 316 m; 47.3% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.97 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (8.1:1; minor axis 3.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-032 · component 939 (near_trace; 4,651 closed / 4,189 emitted px)
Centroid 37.6821°N, 117.5705°W; PCA axis azimuth 20.9° clockwise from north, elongation 3.8:1, axes 17.5 × 4.6 km. Median distance to mapped trace 316 m; 46.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.8:1; minor axis 4.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-033 · component 618 (near_trace; 4,526 closed / 3,904 emitted px)
Centroid 39.3791°N, 117.9695°W; PCA axis azimuth 8.3° clockwise from north, elongation 5.7:1, axes 31.1 × 5.5 km. Median distance to mapped trace 300 m; 53.2% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.7:1; minor axis 5.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-034 · component 617 (near_trace; 4,486 closed / 3,894 emitted px)
Centroid 39.4108°N, 118.5437°W; PCA axis azimuth 17.7° clockwise from north, elongation 7.6:1, axes 24.5 × 3.2 km. Median distance to mapped trace 283 m; 58.5% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (7.6:1; minor axis 3.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-035 · component 358 (near_trace; 4,341 closed / 3,728 emitted px)
Centroid 40.1058°N, 116.9601°W; PCA axis azimuth 36.9° clockwise from north, elongation 3.2:1, axes 20.2 × 6.4 km. Median distance to mapped trace 781 m; 27.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.2:1; minor axis 6.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-036 · component 470 (near_trace; 4,200 closed / 3,663 emitted px)
Centroid 39.8847°N, 119.7576°W; PCA axis azimuth 47.9° clockwise from north, elongation 1.3:1, axes 11.3 × 8.7 km. Median distance to mapped trace 400 m; 42.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 8.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-037 · component 286 (near_trace; 4,162 closed / 3,668 emitted px)
Centroid 40.0905°N, 119.5020°W; PCA axis azimuth 176.5° clockwise from north, elongation 14.1:1, axes 36.6 × 2.6 km. Median distance to mapped trace 316 m; 49.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (14.1:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-038 · component 60 (near_trace; 4,141 closed / 3,646 emitted px)
Centroid 40.5735°N, 118.1035°W; PCA axis azimuth 3.2° clockwise from north, elongation 4.5:1, axes 20.6 × 4.6 km. Median distance to mapped trace 361 m; 45.2% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.94 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.08 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.5:1; minor axis 4.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-039 · component 497 (near_trace; 4,129 closed / 3,811 emitted px)
Centroid 39.7466°N, 118.2641°W; PCA axis azimuth 22.1° clockwise from north, elongation 12.2:1, axes 33.1 × 2.7 km. Median distance to mapped trace 500 m; 31.1% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (12.2:1; minor axis 2.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-040 · component 492 (near_trace; 4,007 closed / 3,396 emitted px)
Centroid 39.7549°N, 119.2132°W; PCA axis azimuth 175.2° clockwise from north, elongation 6.0:1, axes 24.8 × 4.2 km. Median distance to mapped trace 400 m; 41.8% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (6.0:1; minor axis 4.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-041 · component 31 (near_trace; 3,848 closed / 3,406 emitted px)
Centroid 40.6263°N, 117.2353°W; PCA axis azimuth 8.7° clockwise from north, elongation 5.1:1, axes 18.1 × 3.5 km. Median distance to mapped trace 316 m; 48.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.1:1; minor axis 3.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-042 · component 910 (near_trace; 3,687 closed / 3,268 emitted px)
Centroid 37.8647°N, 117.4616°W; PCA axis azimuth 179.6° clockwise from north, elongation 3.4:1, axes 18.7 × 5.5 km. Median distance to mapped trace 990 m; 27.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.4:1; minor axis 5.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-043 · component 526 (near_trace; 3,673 closed / 3,117 emitted px)
Centroid 39.7396°N, 119.1158°W; PCA axis azimuth 34.0° clockwise from north, elongation 5.2:1, axes 19.3 × 3.7 km. Median distance to mapped trace 300 m; 53.9% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.2:1; minor axis 3.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-044 · component 369 (near_trace; 3,634 closed / 3,082 emitted px)
Centroid 40.1037°N, 116.7454°W; PCA axis azimuth 10.5° clockwise from north, elongation 2.3:1, axes 15.4 × 6.6 km. Median distance to mapped trace 671 m; 29.3% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.92 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.09 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 6.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-045 · component 189 (near_trace; 3,564 closed / 3,027 emitted px)
Centroid 40.3389°N, 118.7236°W; PCA axis azimuth 50.9° clockwise from north, elongation 3.3:1, axes 18.2 × 5.5 km. Median distance to mapped trace 283 m; 59.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.3:1; minor axis 5.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-046 · component 476 (near_trace; 3,547 closed / 3,008 emitted px)
Centroid 39.8557°N, 119.9458°W; PCA axis azimuth 175.7° clockwise from north, elongation 1.2:1, axes 9.3 × 7.7 km. Median distance to mapped trace 412 m; 40.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.2:1; minor axis 7.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-047 · component 349 (near_trace; 3,474 closed / 3,085 emitted px)
Centroid 40.1220°N, 117.0798°W; PCA axis azimuth 25.7° clockwise from north, elongation 5.2:1, axes 23.3 × 4.5 km. Median distance to mapped trace 447 m; 33.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.2:1; minor axis 4.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-048 · component 130 (near_trace; 3,403 closed / 3,059 emitted px)
Centroid 40.4180°N, 119.3008°W; PCA axis azimuth 0.9° clockwise from north, elongation 8.1:1, axes 22.4 × 2.8 km. Median distance to mapped trace 361 m; 43.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (8.1:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-049 · component 527 (near_trace; 3,236 closed / 2,743 emitted px)
Centroid 39.7602°N, 118.8597°W; PCA axis azimuth 73.3° clockwise from north, elongation 1.6:1, axes 9.4 × 6.0 km. Median distance to mapped trace 316 m; 48.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 6.0 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-050 · component 851 (near_trace; 3,201 closed / 2,668 emitted px)
Centroid 38.4489°N, 118.1987°W; PCA axis azimuth 123.0° clockwise from north, elongation 2.2:1, axes 11.7 × 5.3 km. Median distance to mapped trace 806 m; 23.7% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.99 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 5.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-051 · component 49 (near_trace; 3,043 closed / 2,683 emitted px)
Centroid 40.5974°N, 117.9502°W; PCA axis azimuth 29.4° clockwise from north, elongation 4.9:1, axes 21.4 × 4.4 km. Median distance to mapped trace 300 m; 53.2% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.05 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.9:1; minor axis 4.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-052 · component 67 (near_trace; 3,031 closed / 2,658 emitted px)
Centroid 40.5182°N, 118.9501°W; PCA axis azimuth 15.6° clockwise from north, elongation 5.8:1, axes 26.1 × 4.5 km. Median distance to mapped trace 316 m; 48.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.8:1; minor axis 4.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-053 · component 215 (near_trace; 2,995 closed / 2,540 emitted px)
Centroid 40.2649°N, 119.4320°W; PCA axis azimuth 16.3° clockwise from north, elongation 7.4:1, axes 19.6 × 2.6 km. Median distance to mapped trace 316 m; 49.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (7.4:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-054 · component 746 (near_trace; 2,892 closed / 2,521 emitted px)
Centroid 39.0062°N, 118.1584°W; PCA axis azimuth 10.0° clockwise from north, elongation 4.3:1, axes 17.1 × 4.0 km. Median distance to mapped trace 316 m; 48.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.90 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.3:1; minor axis 4.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-055 · component 632 (near_trace; 2,889 closed / 2,197 emitted px)
Centroid 39.3899°N, 119.1250°W; PCA axis azimuth 103.0° clockwise from north, elongation 2.8:1, axes 13.7 × 4.9 km. Median distance to mapped trace 361 m; 45.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 4.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-056 · component 467 (near_trace; 2,831 closed / 2,593 emitted px)
Centroid 39.9160°N, 118.6264°W; PCA axis azimuth 52.5° clockwise from north, elongation 2.9:1, axes 13.3 × 4.7 km. Median distance to mapped trace 632 m; 27.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 4.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-057 · component 327 (near_trace; 2,815 closed / 2,366 emitted px)
Centroid 40.1560°N, 117.2325°W; PCA axis azimuth 26.4° clockwise from north, elongation 1.5:1, axes 12.2 × 8.4 km. Median distance to mapped trace 400 m; 42.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 8.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-058 · component 289 (near_trace; 2,811 closed / 2,294 emitted px)
Centroid 40.2382°N, 117.0529°W; PCA axis azimuth 84.4° clockwise from north, elongation 1.4:1, axes 9.2 × 6.4 km. Median distance to mapped trace 995 m; 19.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 6.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-059 · component 520 (near_trace; 2,727 closed / 2,392 emitted px)
Centroid 39.7874°N, 118.6724°W; PCA axis azimuth 70.2° clockwise from north, elongation 2.0:1, axes 8.9 × 4.4 km. Median distance to mapped trace 224 m; 66.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 4.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-060 · component 323 (near_trace; 2,637 closed / 2,291 emitted px)
Centroid 40.1603°N, 119.2134°W; PCA axis azimuth 5.9° clockwise from north, elongation 3.3:1, axes 13.1 × 4.0 km. Median distance to mapped trace 361 m; 45.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.3:1; minor axis 4.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-061 · component 578 (near_trace; 2,616 closed / 2,252 emitted px)
Centroid 39.5437°N, 118.0113°W; PCA axis azimuth 14.3° clockwise from north, elongation 1.3:1, axes 9.4 × 7.5 km. Median distance to mapped trace 300 m; 53.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 7.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-062 · component 273 (near_trace; 2,579 closed / 2,207 emitted px)
Centroid 40.2311°N, 119.6964°W; PCA axis azimuth 123.8° clockwise from north, elongation 2.3:1, axes 9.6 × 4.2 km. Median distance to mapped trace 224 m; 62.3% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 4.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-063 · component 70 (near_trace; 2,578 closed / 2,294 emitted px)
Centroid 40.5978°N, 117.6240°W; PCA axis azimuth 171.6° clockwise from north, elongation 3.3:1, axes 12.4 × 3.7 km. Median distance to mapped trace 316 m; 47.7% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.3:1; minor axis 3.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-064 · component 463 (near_trace; 2,529 closed / 2,148 emitted px)
Centroid 39.9355°N, 118.9931°W; PCA axis azimuth 58.9° clockwise from north, elongation 1.7:1, axes 10.1 × 5.9 km. Median distance to mapped trace 424 m; 40.0% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 5.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-065 · component 821 (near_trace; 2,509 closed / 2,235 emitted px)
Centroid 38.6289°N, 118.2143°W; PCA axis azimuth 142.4° clockwise from north, elongation 10.7:1, axes 22.3 × 2.1 km. Median distance to mapped trace 283 m; 55.6% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.97 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (10.7:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-066 · component 772 (near_trace; 2,499 closed / 2,154 emitted px)
Centroid 38.8783°N, 118.2336°W; PCA axis azimuth 72.0° clockwise from north, elongation 2.5:1, axes 9.4 × 3.8 km. Median distance to mapped trace 283 m; 53.8% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.98 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 3.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-067 · component 391 (near_trace; 2,496 closed / 2,196 emitted px)
Centroid 40.0958°N, 116.8780°W; PCA axis azimuth 36.2° clockwise from north, elongation 2.8:1, axes 12.9 × 4.7 km. Median distance to mapped trace 671 m; 24.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 4.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-068 · component 17 (near_trace; 2,468 closed / 2,116 emitted px)
Centroid 40.7012°N, 116.8189°W; PCA axis azimuth 88.8° clockwise from north, elongation 2.8:1, axes 17.6 × 6.3 km. Median distance to mapped trace 316 m; 49.7% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 6.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-069 · component 94 (near_trace; 2,395 closed / 2,115 emitted px)
Centroid 40.4936°N, 119.6054°W; PCA axis azimuth 24.0° clockwise from north, elongation 6.4:1, axes 22.1 × 3.5 km. Median distance to mapped trace 316 m; 47.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (6.4:1; minor axis 3.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-070 · component 765 (near_trace; 2,387 closed / 2,030 emitted px)
Centroid 38.8678°N, 117.9164°W; PCA axis azimuth 16.2° clockwise from north, elongation 7.9:1, axes 17.8 × 2.2 km. Median distance to mapped trace 283 m; 59.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (7.9:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-071 · component 374 (near_trace; 2,384 closed / 2,041 emitted px)
Centroid 40.1172°N, 116.1692°W; PCA axis azimuth 6.8° clockwise from north, elongation 3.5:1, axes 14.2 × 4.0 km. Median distance to mapped trace 583 m; 30.4% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.97 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.00 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.5:1; minor axis 4.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-072 · component 648 (near_trace; 2,381 closed / 2,010 emitted px)
Centroid 39.3347°N, 119.4563°W; PCA axis azimuth 36.1° clockwise from north, elongation 1.4:1, axes 11.6 × 8.6 km. Median distance to mapped trace 500 m; 39.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 8.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-073 · component 677 (near_trace; 2,347 closed / 2,008 emitted px)
Centroid 39.2372°N, 119.3335°W; PCA axis azimuth 84.6° clockwise from north, elongation 1.4:1, axes 7.8 × 5.6 km. Median distance to mapped trace 539 m; 30.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 5.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-074 · component 480 (near_trace; 2,293 closed / 1,939 emitted px)
Centroid 39.8316°N, 119.8665°W; PCA axis azimuth 5.2° clockwise from north, elongation 3.6:1, axes 13.2 × 3.6 km. Median distance to mapped trace 900 m; 21.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.6:1; minor axis 3.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-075 · component 171 (near_trace; 2,288 closed / 1,994 emitted px)
Centroid 40.3705°N, 119.2462°W; PCA axis azimuth 22.6° clockwise from north, elongation 5.3:1, axes 15.2 × 2.9 km. Median distance to mapped trace 412 m; 37.2% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.95 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.3:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-076 · component 343 (near_trace; 2,284 closed / 1,909 emitted px)
Centroid 40.1660°N, 116.8344°W; PCA axis azimuth 125.7° clockwise from north, elongation 1.5:1, axes 10.5 × 7.1 km. Median distance to mapped trace 860 m; 32.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 7.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-077 · component 503 (near_trace; 2,201 closed / 1,897 emitted px)
Centroid 39.7979°N, 119.8067°W; PCA axis azimuth 44.1° clockwise from north, elongation 2.1:1, axes 9.4 × 4.5 km. Median distance to mapped trace 400 m; 42.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 4.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-078 · component 725 (near_trace; 2,175 closed / 1,909 emitted px)
Centroid 39.0998°N, 118.4132°W; PCA axis azimuth 176.7° clockwise from north, elongation 1.7:1, axes 8.5 × 5.0 km. Median distance to mapped trace 283 m; 61.1% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.91 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 5.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-079 · component 881 (near_trace; 2,165 closed / 1,916 emitted px)
Centroid 38.0975°N, 117.8839°W; PCA axis azimuth 179.1° clockwise from north, elongation 3.8:1, axes 10.8 × 2.9 km. Median distance to mapped trace 300 m; 55.3% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.8:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-080 · component 474 (near_trace; 2,111 closed / 1,891 emitted px)
Centroid 39.8913°N, 119.0983°W; PCA axis azimuth 176.7° clockwise from north, elongation 1.6:1, axes 8.7 × 5.4 km. Median distance to mapped trace 447 m; 37.4% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 5.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-081 · component 11 (near_trace; 2,100 closed / 1,862 emitted px)
Centroid 40.6896°N, 117.6474°W; PCA axis azimuth 152.8° clockwise from north, elongation 3.0:1, axes 10.2 × 3.4 km. Median distance to mapped trace 447 m; 36.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.0:1; minor axis 3.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-082 · component 668 (near_trace; 2,095 closed / 1,787 emitted px)
Centroid 39.2845°N, 118.4888°W; PCA axis azimuth 59.8° clockwise from north, elongation 1.4:1, axes 7.3 × 5.2 km. Median distance to mapped trace 283 m; 58.8% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 5.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-083 · component 336 (near_trace; 2,062 closed / 1,804 emitted px)
Centroid 40.1495°N, 117.8535°W; PCA axis azimuth 26.5° clockwise from north, elongation 3.9:1, axes 14.3 × 3.7 km. Median distance to mapped trace 316 m; 47.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.9:1; minor axis 3.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-084 · component 575 (near_trace; 2,059 closed / 1,818 emitted px)
Centroid 39.5756°N, 118.4833°W; PCA axis azimuth 157.0° clockwise from north, elongation 1.3:1, axes 6.2 × 4.9 km. Median distance to mapped trace 316 m; 46.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 4.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-085 · component 786 (near_trace; 1,979 closed / 1,649 emitted px)
Centroid 38.7876°N, 118.0144°W; PCA axis azimuth 172.6° clockwise from north, elongation 3.1:1, axes 9.4 × 3.1 km. Median distance to mapped trace 300 m; 50.3% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.1:1; minor axis 3.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-086 · component 691 (near_trace; 1,973 closed / 1,589 emitted px)
Centroid 39.1916°N, 118.9777°W; PCA axis azimuth 1.2° clockwise from north, elongation 1.9:1, axes 11.1 × 5.8 km. Median distance to mapped trace 400 m; 42.9% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 5.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-087 · component 897 (near_trace; 1,931 closed / 1,693 emitted px)
Centroid 38.0054°N, 118.1106°W; PCA axis azimuth 96.5° clockwise from north, elongation 3.8:1, axes 11.2 × 2.9 km. Median distance to mapped trace 400 m; 43.0% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.8:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-088 · component 909 (near_trace; 1,922 closed / 1,698 emitted px)
Centroid 37.9171°N, 118.3686°W; PCA axis azimuth 47.1° clockwise from north, elongation 2.3:1, axes 8.5 × 3.8 km. Median distance to mapped trace 300 m; 50.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 3.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-089 · component 768 (near_trace; 1,895 closed / 1,577 emitted px)
Centroid 38.8744°N, 118.5666°W; PCA axis azimuth 3.2° clockwise from north, elongation 2.0:1, axes 8.8 × 4.3 km. Median distance to mapped trace 583 m; 27.5% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 4.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-090 · component 97 (near_trace; 1,874 closed / 1,626 emitted px)
Centroid 40.5174°N, 118.9938°W; PCA axis azimuth 19.0° clockwise from north, elongation 5.3:1, axes 15.8 × 3.0 km. Median distance to mapped trace 300 m; 53.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.3:1; minor axis 3.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-091 · component 164 (near_trace; 1,809 closed / 1,577 emitted px)
Centroid 40.3946°N, 119.3895°W; PCA axis azimuth 173.3° clockwise from north, elongation 3.9:1, axes 10.1 × 2.6 km. Median distance to mapped trace 300 m; 56.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.9:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-092 · component 178 (near_trace; 1,783 closed / 1,561 emitted px)
Centroid 40.3571°N, 118.8289°W; PCA axis azimuth 13.4° clockwise from north, elongation 5.5:1, axes 14.5 × 2.6 km. Median distance to mapped trace 300 m; 50.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.05 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.5:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-093 · component 710 (near_trace; 1,752 closed / 1,536 emitted px)
Centroid 39.1475°N, 118.0774°W; PCA axis azimuth 28.7° clockwise from north, elongation 1.4:1, axes 7.8 × 5.6 km. Median distance to mapped trace 361 m; 45.3% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.95 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.90 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 5.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-094 · component 721 (near_trace; 1,739 closed / 1,560 emitted px)
Centroid 39.1244°N, 118.2309°W; PCA axis azimuth 166.4° clockwise from north, elongation 2.9:1, axes 8.5 × 2.9 km. Median distance to mapped trace 316 m; 47.3% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-095 · component 515 (near_trace; 1,738 closed / 1,530 emitted px)
Centroid 39.7750°N, 119.7112°W; PCA axis azimuth 110.7° clockwise from north, elongation 2.6:1, axes 11.9 × 4.5 km. Median distance to mapped trace 1204 m; 18.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.95 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.90 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 4.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-096 · component 792 (near_trace; 1,698 closed / 1,474 emitted px)
Centroid 38.7495°N, 117.8228°W; PCA axis azimuth 164.2° clockwise from north, elongation 8.1:1, axes 18.2 × 2.2 km. Median distance to mapped trace 283 m; 60.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (8.1:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-097 · component 899 (near_trace; 1,692 closed / 1,408 emitted px)
Centroid 37.9828°N, 117.4339°W; PCA axis azimuth 5.4° clockwise from north, elongation 2.5:1, axes 10.3 × 4.2 km. Median distance to mapped trace 300 m; 51.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 4.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-098 · component 177 (near_trace; 1,629 closed / 1,486 emitted px)
Centroid 40.3530°N, 119.6483°W; PCA axis azimuth 168.3° clockwise from north, elongation 6.4:1, axes 12.6 × 2.0 km. Median distance to mapped trace 400 m; 40.8% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-099 · component 732 (near_trace; 1,577 closed / 1,329 emitted px)
Centroid 39.0950°N, 118.1020°W; PCA axis azimuth 154.5° clockwise from north, elongation 3.3:1, axes 10.2 × 3.1 km. Median distance to mapped trace 300 m; 50.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.3:1; minor axis 3.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-100 · component 76 (near_trace; 1,541 closed / 1,347 emitted px)
Centroid 40.5877°N, 117.4786°W; PCA axis azimuth 19.8° clockwise from north, elongation 4.0:1, axes 11.5 × 2.9 km. Median distance to mapped trace 224 m; 61.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.0:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-101 · component 168 (near_trace; 1,537 closed / 1,365 emitted px)
Centroid 40.4233°N, 118.6833°W; PCA axis azimuth 44.9° clockwise from north, elongation 2.4:1, axes 7.2 × 3.1 km. Median distance to mapped trace 300 m; 51.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 3.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-102 · component 41 (near_trace; 1,536 closed / 1,349 emitted px)
Centroid 40.6274°N, 119.1401°W; PCA axis azimuth 19.5° clockwise from north, elongation 3.1:1, axes 9.1 × 2.9 km. Median distance to mapped trace 361 m; 44.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.1:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-103 · component 666 (near_trace; 1,528 closed / 1,378 emitted px)
Centroid 39.2963°N, 118.8578°W; PCA axis azimuth 130.1° clockwise from north, elongation 3.8:1, axes 9.6 × 2.5 km. Median distance to mapped trace 316 m; 46.9% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.8:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-104 · component 789 (near_trace; 1,511 closed / 1,282 emitted px)
Centroid 38.7759°N, 118.2065°W; PCA axis azimuth 157.7° clockwise from north, elongation 5.1:1, axes 13.6 × 2.7 km. Median distance to mapped trace 400 m; 41.8% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.1:1; minor axis 2.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-105 · component 790 (near_trace; 1,498 closed / 1,270 emitted px)
Centroid 38.7600°N, 118.3466°W; PCA axis azimuth 145.3° clockwise from north, elongation 5.5:1, axes 15.8 × 2.9 km. Median distance to mapped trace 1528 m; 24.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.91 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.5:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-106 · component 420 (near_trace; 1,494 closed / 1,312 emitted px)
Centroid 40.0665°N, 116.4160°W; PCA axis azimuth 66.6° clockwise from north, elongation 6.1:1, axes 13.6 × 2.2 km. Median distance to mapped trace 283 m; 61.2% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.03 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (6.1:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-107 · component 835 (near_trace; 1,476 closed / 1,248 emitted px)
Centroid 38.6033°N, 118.2484°W; PCA axis azimuth 135.8° clockwise from north, elongation 3.6:1, axes 9.0 × 2.5 km. Median distance to mapped trace 283 m; 53.9% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.96 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.6:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-108 · component 183 (near_trace; 1,465 closed / 1,341 emitted px)
Centroid 40.3724°N, 119.0484°W; PCA axis azimuth 41.9° clockwise from north, elongation 5.6:1, axes 11.2 × 2.0 km. Median distance to mapped trace 361 m; 41.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 1.00 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-109 · component 661 (near_trace; 1,431 closed / 1,185 emitted px)
Centroid 39.3243°N, 118.2448°W; PCA axis azimuth 12.5° clockwise from north, elongation 2.4:1, axes 8.7 × 3.7 km. Median distance to mapped trace 316 m; 48.9% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.96 regional percentile of the component median), geodetic shear rate (geod_shearrate, high 0.91 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 3.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-110 · component 834 (near_trace; 1,355 closed / 1,227 emitted px)
Centroid 38.5997°N, 118.3333°W; PCA axis azimuth 143.9° clockwise from north, elongation 6.7:1, axes 11.7 × 1.7 km. Median distance to mapped trace 316 m; 49.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.97 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-111 · component 356 (near_trace; 1,341 closed / 1,114 emitted px)
Centroid 40.1638°N, 117.7339°W; PCA axis azimuth 137.6° clockwise from north, elongation 1.3:1, axes 6.7 × 5.1 km. Median distance to mapped trace 1118 m; 24.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.95 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 5.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-112 · component 683 (near_trace; 1,330 closed / 1,128 emitted px)
Centroid 39.2375°N, 119.0323°W; PCA axis azimuth 78.1° clockwise from north, elongation 3.3:1, axes 9.2 × 2.8 km. Median distance to mapped trace 283 m; 57.6% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.3:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-113 · component 477 (near_trace; 1,302 closed / 1,090 emitted px)
Centroid 39.8902°N, 119.1567°W; PCA axis azimuth 21.8° clockwise from north, elongation 1.4:1, axes 5.4 × 3.9 km. Median distance to mapped trace 283 m; 53.7% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 3.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-114 · component 947 (near_trace; 1,248 closed / 1,106 emitted px)
Centroid 37.6741°N, 117.9650°W; PCA axis azimuth 2.3° clockwise from north, elongation 3.8:1, axes 9.9 × 2.6 km. Median distance to mapped trace 300 m; 53.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.8:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-115 · component 496 (near_trace; 1,236 closed / 1,125 emitted px)
Centroid 39.8194°N, 119.7375°W; PCA axis azimuth 134.8° clockwise from north, elongation 1.1:1, axes 5.7 × 5.1 km. Median distance to mapped trace 412 m; 39.4% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 5.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-116 · component 511 (near_trace; 1,236 closed / 1,072 emitted px)
Centroid 39.7932°N, 118.9890°W; PCA axis azimuth 29.0° clockwise from north, elongation 1.9:1, axes 6.1 × 3.1 km. Median distance to mapped trace 539 m; 26.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 3.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-117 · component 534 (near_trace; 1,207 closed / 1,040 emitted px)
Centroid 39.7323°N, 119.2661°W; PCA axis azimuth 169.0° clockwise from north, elongation 2.0:1, axes 6.5 × 3.2 km. Median distance to mapped trace 539 m; 31.2% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 3.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-118 · component 91 (near_trace; 1,191 closed / 1,009 emitted px)
Centroid 40.5616°N, 119.0919°W; PCA axis azimuth 13.8° clockwise from north, elongation 2.3:1, axes 6.2 × 2.7 km. Median distance to mapped trace 316 m; 49.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 2.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-119 · component 728 (near_trace; 1,171 closed / 976 emitted px)
Centroid 39.0896°N, 118.7032°W; PCA axis azimuth 141.0° clockwise from north, elongation 5.5:1, axes 11.7 × 2.1 km. Median distance to mapped trace 361 m; 43.2% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.5:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-120 · component 777 (near_trace; 1,158 closed / 976 emitted px)
Centroid 38.8554°N, 118.5017°W; PCA axis azimuth 128.9° clockwise from north, elongation 1.9:1, axes 6.5 × 3.4 km. Median distance to mapped trace 500 m; 35.5% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 3.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-121 · component 147 (near_trace; 1,136 closed / 1,001 emitted px)
Centroid 40.4429°N, 118.1072°W; PCA axis azimuth 176.7° clockwise from north, elongation 4.2:1, axes 9.3 × 2.2 km. Median distance to mapped trace 300 m; 59.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (4.2:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-122 · component 858 (near_trace; 1,125 closed / 1,013 emitted px)
Centroid 38.4328°N, 117.9865°W; PCA axis azimuth 39.0° clockwise from north, elongation 1.5:1, axes 5.6 × 3.7 km. Median distance to mapped trace 539 m; 30.3% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.94 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 3.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-123 · component 799 (near_trace; 1,119 closed / 858 emitted px)
Centroid 38.7548°N, 118.3983°W; PCA axis azimuth 150.1° clockwise from north, elongation 2.5:1, axes 7.0 × 2.8 km. Median distance to mapped trace 224 m; 64.9% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-124 · component 241 (near_trace; 1,109 closed / 954 emitted px)
Centroid 40.3076°N, 117.0565°W; PCA axis azimuth 34.0° clockwise from north, elongation 1.7:1, axes 5.8 × 3.4 km. Median distance to mapped trace 500 m; 31.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 3.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-125 · component 431 (near_trace; 1,095 closed / 933 emitted px)
Centroid 40.0483°N, 117.6213°W; PCA axis azimuth 37.5° clockwise from north, elongation 2.3:1, axes 6.0 × 2.6 km. Median distance to mapped trace 224 m; 61.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-126 · component 169 (near_trace; 1,092 closed / 924 emitted px)
Centroid 40.4388°N, 116.4694°W; PCA axis azimuth 54.3° clockwise from north, elongation 5.6:1, axes 11.8 × 2.1 km. Median distance to mapped trace 224 m; 66.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (5.6:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-127 · component 481 (near_trace; 1,091 closed / 943 emitted px)
Centroid 39.9067°N, 118.5162°W; PCA axis azimuth 84.5° clockwise from north, elongation 3.3:1, axes 8.1 × 2.5 km. Median distance to mapped trace 283 m; 61.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.3:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-128 · component 191 (near_trace; 1,067 closed / 950 emitted px)
Centroid 40.3580°N, 118.9419°W; PCA axis azimuth 26.4° clockwise from north, elongation 4.8:1, axes 9.1 × 1.9 km. Median distance to mapped trace 510 m; 29.7% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-129 · component 715 (near_trace; 1,053 closed / 879 emitted px)
Centroid 39.1444°N, 118.5853°W; PCA axis azimuth 170.2° clockwise from north, elongation 1.8:1, axes 5.4 × 3.0 km. Median distance to mapped trace 361 m; 43.1% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 3.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-130 · component 298 (near_trace; 1,047 closed / 949 emitted px)
Centroid 40.2270°N, 118.1636°W; PCA axis azimuth 25.9° clockwise from north, elongation 5.3:1, axes 9.1 × 1.7 km. Median distance to mapped trace 300 m; 52.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-131 · component 251 (near_trace; 1,034 closed / 919 emitted px)
Centroid 40.2747°N, 119.0678°W; PCA axis azimuth 28.3° clockwise from north, elongation 4.0:1, axes 7.9 × 2.0 km. Median distance to mapped trace 361 m; 44.4% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.03 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-132 · component 432 (near_trace; 1,023 closed / 873 emitted px)
Centroid 40.0410°N, 118.0151°W; PCA axis azimuth 35.0° clockwise from north, elongation 3.8:1, axes 8.1 × 2.1 km. Median distance to mapped trace 424 m; 37.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.8:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-133 · component 6 (near_trace; 1,016 closed / 889 emitted px)
Centroid 40.6693°N, 119.0657°W; PCA axis azimuth 35.0° clockwise from north, elongation 5.5:1, axes 10.8 × 2.0 km. Median distance to mapped trace 361 m; 46.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-134 · component 141 (near_trace; 1,008 closed / 879 emitted px)
Centroid 40.4596°N, 118.0544°W; PCA axis azimuth 179.7° clockwise from north, elongation 7.6:1, axes 10.3 × 1.4 km. Median distance to mapped trace 300 m; 62.3% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-135 · component 185 (near_trace; 999 closed / 886 emitted px)
Centroid 40.3711°N, 118.8552°W; PCA axis azimuth 6.5° clockwise from north, elongation 4.7:1, axes 9.0 × 1.9 km. Median distance to mapped trace 500 m; 30.5% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.99 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.05 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-136 · component 701 (near_trace; 998 closed / 871 emitted px)
Centroid 39.1812°N, 119.2020°W; PCA axis azimuth 13.3° clockwise from north, elongation 1.8:1, axes 5.2 × 2.9 km. Median distance to mapped trace 300 m; 53.5% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-137 · component 613 (near_trace; 981 closed / 805 emitted px)
Centroid 39.4777°N, 118.4568°W; PCA axis azimuth 34.0° clockwise from north, elongation 2.7:1, axes 7.5 × 2.8 km. Median distance to mapped trace 400 m; 41.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-138 · component 812 (near_trace; 964 closed / 836 emitted px)
Centroid 38.6979°N, 118.3362°W; PCA axis azimuth 134.8° clockwise from north, elongation 4.4:1, axes 8.4 × 1.9 km. Median distance to mapped trace 283 m; 57.3% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.94 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-139 · component 569 (near_trace; 941 closed / 822 emitted px)
Centroid 39.5804°N, 119.3811°W; PCA axis azimuth 100.6° clockwise from north, elongation 2.8:1, axes 7.7 × 2.8 km. Median distance to mapped trace 412 m; 35.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-140 · component 363 (isolated; 934 closed / 833 emitted px)
Centroid 40.1309°N, 119.3803°W; PCA axis azimuth 4.0° clockwise from north, elongation 4.2:1, axes 10.0 × 2.4 km. Median distance to mapped trace 6619 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (4.2:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-141 · component 316 (near_trace; 919 closed / 746 emitted px)
Centroid 40.1992°N, 119.1606°W; PCA axis azimuth 5.8° clockwise from north, elongation 2.4:1, axes 6.3 × 2.6 km. Median distance to mapped trace 283 m; 60.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-142 · component 698 (near_trace; 916 closed / 789 emitted px)
Centroid 39.1917°N, 118.5551°W; PCA axis azimuth 2.7° clockwise from north, elongation 1.9:1, axes 5.3 × 2.9 km. Median distance to mapped trace 300 m; 50.6% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-143 · component 522 (near_trace; 914 closed / 792 emitted px)
Centroid 39.7877°N, 119.1453°W; PCA axis azimuth 68.4° clockwise from north, elongation 1.7:1, axes 6.4 × 3.8 km. Median distance to mapped trace 600 m; 26.6% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 3.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-144 · component 595 (near_trace; 912 closed / 768 emitted px)
Centroid 39.5254°N, 119.0011°W; PCA axis azimuth 73.6° clockwise from north, elongation 2.6:1, axes 6.7 × 2.5 km. Median distance to mapped trace 224 m; 63.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-145 · component 344 (near_trace; 903 closed / 742 emitted px)
Centroid 40.1831°N, 118.3109°W; PCA axis azimuth 25.7° clockwise from north, elongation 2.4:1, axes 5.8 × 2.4 km. Median distance to mapped trace 200 m; 68.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-146 · component 689 (near_trace; 812 closed / 716 emitted px)
Centroid 39.2081°N, 118.3980°W; PCA axis azimuth 16.8° clockwise from north, elongation 3.9:1, axes 7.4 × 1.9 km. Median distance to mapped trace 316 m; 48.7% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.93 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-147 · component 437 (near_trace; 801 closed / 730 emitted px)
Centroid 40.0282°N, 119.0509°W; PCA axis azimuth 17.0° clockwise from north, elongation 2.8:1, axes 6.1 × 2.1 km. Median distance to mapped trace 500 m; 30.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-148 · component 749 (near_trace; 799 closed / 665 emitted px)
Centroid 39.0151°N, 118.4866°W; PCA axis azimuth 0.2° clockwise from north, elongation 5.7:1, axes 8.8 × 1.6 km. Median distance to mapped trace 224 m; 65.7% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.91 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.96 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-149 · component 706 (near_trace; 765 closed / 679 emitted px)
Centroid 39.1876°N, 118.2135°W; PCA axis azimuth 62.5° clockwise from north, elongation 1.4:1, axes 4.6 × 3.2 km. Median distance to mapped trace 985 m; 17.5% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 3.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-150 · component 33 (near_trace; 763 closed / 669 emitted px)
Centroid 40.6904°N, 117.1266°W; PCA axis azimuth 72.9° clockwise from north, elongation 2.5:1, axes 8.0 × 3.2 km. Median distance to mapped trace 500 m; 36.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 3.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-151 · component 594 (near_trace; 763 closed / 689 emitted px)
Centroid 39.5121°N, 119.6242°W; PCA axis azimuth 9.4° clockwise from north, elongation 1.3:1, axes 3.8 × 2.9 km. Median distance to mapped trace 671 m; 19.3% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 2.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-152 · component 521 (near_trace; 759 closed / 689 emitted px)
Centroid 39.7658°N, 119.6408°W; PCA axis azimuth 156.4° clockwise from north, elongation 4.9:1, axes 7.9 × 1.6 km. Median distance to mapped trace 361 m; 46.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-153 · component 550 (near_trace; 708 closed / 599 emitted px)
Centroid 39.6643°N, 119.6684°W; PCA axis azimuth 175.7° clockwise from north, elongation 3.5:1, axes 6.3 × 1.8 km. Median distance to mapped trace 361 m; 45.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-154 · component 875 (near_trace; 696 closed / 625 emitted px)
Centroid 38.2557°N, 117.8172°W; PCA axis azimuth 148.2° clockwise from north, elongation 4.0:1, axes 6.3 × 1.6 km. Median distance to mapped trace 300 m; 51.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-155 · component 238 (near_trace; 694 closed / 595 emitted px)
Centroid 40.2930°N, 119.5906°W; PCA axis azimuth 142.2° clockwise from north, elongation 1.1:1, axes 3.4 × 3.0 km. Median distance to mapped trace 224 m; 65.0% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 3.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-156 · component 416 (near_trace; 693 closed / 589 emitted px)
Centroid 40.0747°N, 117.3448°W; PCA axis azimuth 40.0° clockwise from north, elongation 2.7:1, axes 5.3 × 1.9 km. Median distance to mapped trace 224 m; 73.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-157 · component 464 (near_trace; 691 closed / 610 emitted px)
Centroid 39.9528°N, 118.9281°W; PCA axis azimuth 3.5° clockwise from north, elongation 1.8:1, axes 4.5 × 2.5 km. Median distance to mapped trace 412 m; 40.8% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-158 · component 7 (near_trace; 686 closed / 586 emitted px)
Centroid 40.6870°N, 118.9302°W; PCA axis azimuth 12.4° clockwise from north, elongation 2.4:1, axes 5.2 × 2.1 km. Median distance to mapped trace 447 m; 35.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-159 · component 953 (near_trace; 682 closed / 574 emitted px)
Centroid 37.5988°N, 117.6525°W; PCA axis azimuth 56.0° clockwise from north, elongation 4.9:1, axes 8.3 × 1.7 km. Median distance to mapped trace 224 m; 69.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-160 · component 478 (near_trace; 680 closed / 595 emitted px)
Centroid 39.9053°N, 119.2157°W; PCA axis azimuth 68.0° clockwise from north, elongation 2.0:1, axes 4.4 × 2.1 km. Median distance to mapped trace 583 m; 30.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-161 · component 224 (near_trace; 678 closed / 583 emitted px)
Centroid 40.3480°N, 116.5090°W; PCA axis azimuth 177.3° clockwise from north, elongation 1.4:1, axes 4.0 × 2.8 km. Median distance to mapped trace 224 m; 68.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-162 · component 561 (isolated; 673 closed / 583 emitted px)
Centroid 39.6026°N, 119.3982°W; PCA axis azimuth 83.6° clockwise from north, elongation 2.4:1, axes 5.2 × 2.2 km. Median distance to mapped trace 1726 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-163 · component 301 (isolated; 671 closed / 591 emitted px)
Centroid 40.2189°N, 119.3939°W; PCA axis azimuth 177.2° clockwise from north, elongation 2.3:1, axes 5.2 × 2.2 km. Median distance to mapped trace 3400 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-164 · component 48 (halo; 662 closed / 509 emitted px)
Centroid 40.6611°N, 116.2571°W; PCA axis azimuth 163.9° clockwise from north, elongation 2.1:1, axes 4.4 × 2.1 km. Median distance to mapped trace 200 m; 84.3% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.02 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-165 · component 8 (near_trace; 647 closed / 583 emitted px)
Centroid 40.6875°N, 118.8982°W; PCA axis azimuth 25.7° clockwise from north, elongation 4.2:1, axes 6.4 × 1.5 km. Median distance to mapped trace 283 m; 58.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-166 · component 209 (near_trace; 646 closed / 556 emitted px)
Centroid 40.3560°N, 117.8267°W; PCA axis azimuth 18.3° clockwise from north, elongation 2.5:1, axes 5.5 × 2.1 km. Median distance to mapped trace 361 m; 43.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-167 · component 802 (near_trace; 646 closed / 554 emitted px)
Centroid 38.7650°N, 118.5907°W; PCA axis azimuth 13.0° clockwise from north, elongation 2.2:1, axes 4.5 × 2.1 km. Median distance to mapped trace 500 m; 37.0% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-168 · component 53 (near_trace; 643 closed / 513 emitted px)
Centroid 40.6433°N, 117.5358°W; PCA axis azimuth 169.7° clockwise from north, elongation 3.3:1, axes 6.1 × 1.9 km. Median distance to mapped trace 412 m; 36.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-169 · component 907 (near_trace; 636 closed / 553 emitted px)
Centroid 37.9425°N, 117.3767°W; PCA axis azimuth 29.4° clockwise from north, elongation 3.7:1, axes 7.1 × 1.9 km. Median distance to mapped trace 224 m; 62.9% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.10 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-170 · component 845 (near_trace; 617 closed / 518 emitted px)
Centroid 38.5192°N, 117.7628°W; PCA axis azimuth 153.6° clockwise from north, elongation 2.8:1, axes 6.1 × 2.1 km. Median distance to mapped trace 361 m; 42.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-171 · component 577 (near_trace; 611 closed / 517 emitted px)
Centroid 39.5692°N, 118.7451°W; PCA axis azimuth 150.6° clockwise from north, elongation 3.7:1, axes 6.2 × 1.6 km. Median distance to mapped trace 283 m; 61.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-172 · component 844 (near_trace; 607 closed / 510 emitted px)
Centroid 38.5190°N, 118.1276°W; PCA axis azimuth 175.5° clockwise from north, elongation 2.6:1, axes 5.1 × 1.9 km. Median distance to mapped trace 361 m; 43.9% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.96 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.98 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-173 · component 686 (near_trace; 606 closed / 546 emitted px)
Centroid 39.2238°N, 119.1431°W; PCA axis azimuth 0.9° clockwise from north, elongation 1.3:1, axes 3.5 × 2.6 km. Median distance to mapped trace 316 m; 48.4% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.93 regional percentile of the component median), magnetic gradient/contact (mag_hgm, high 0.94 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.92 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 2.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-174 · component 283 (near_trace; 597 closed / 530 emitted px)
Centroid 40.2408°N, 119.2889°W; PCA axis azimuth 169.3° clockwise from north, elongation 2.1:1, axes 4.2 × 2.0 km. Median distance to mapped trace 500 m; 29.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-175 · component 519 (near_trace; 591 closed / 518 emitted px)
Centroid 39.7944°N, 119.2693°W; PCA axis azimuth 161.6° clockwise from north, elongation 1.0:1, axes 2.8 × 2.8 km. Median distance to mapped trace 224 m; 67.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.0:1; minor axis 2.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-176 · component 660 (near_trace; 587 closed / 512 emitted px)
Centroid 39.3400°N, 118.5166°W; PCA axis azimuth 151.2° clockwise from north, elongation 2.8:1, axes 4.7 × 1.7 km. Median distance to mapped trace 224 m; 69.9% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.93 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.94 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-177 · component 159 (near_trace; 583 closed / 535 emitted px)
Centroid 40.4390°N, 118.7757°W; PCA axis azimuth 26.3° clockwise from north, elongation 2.7:1, axes 5.3 × 1.9 km. Median distance to mapped trace 600 m; 27.3% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-178 · component 242 (near_trace; 579 closed / 487 emitted px)
Centroid 40.2836°N, 119.7996°W; PCA axis azimuth 155.2° clockwise from north, elongation 2.4:1, axes 5.5 × 2.3 km. Median distance to mapped trace 400 m; 43.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 2.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-179 · component 318 (near_trace; 566 closed / 515 emitted px)
Centroid 40.2178°N, 117.8732°W; PCA axis azimuth 18.6° clockwise from north, elongation 2.8:1, axes 4.9 × 1.8 km. Median distance to mapped trace 361 m; 40.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-180 · component 158 (near_trace; 554 closed / 491 emitted px)
Centroid 40.4529°N, 117.4010°W; PCA axis azimuth 19.8° clockwise from north, elongation 3.0:1, axes 4.7 × 1.6 km. Median distance to mapped trace 224 m; 70.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-181 · component 451 (isolated; 549 closed / 526 emitted px)
Centroid 40.0079°N, 118.6871°W; PCA axis azimuth 179.3° clockwise from north, elongation 3.9:1, axes 6.7 × 1.7 km. Median distance to mapped trace 1916 m; 0.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-182 · component 2 (near_trace; 548 closed / 484 emitted px)
Centroid 40.6801°N, 119.2139°W; PCA axis azimuth 178.1° clockwise from north, elongation 3.5:1, axes 5.6 × 1.6 km. Median distance to mapped trace 316 m; 49.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-183 · component 490 (near_trace; 547 closed / 475 emitted px)
Centroid 39.8610°N, 119.3627°W; PCA axis azimuth 69.5° clockwise from north, elongation 1.5:1, axes 3.6 × 2.5 km. Median distance to mapped trace 283 m; 52.8% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-184 · component 101 (near_trace; 544 closed / 463 emitted px)
Centroid 40.5697°N, 117.6557°W; PCA axis azimuth 139.8° clockwise from north, elongation 2.3:1, axes 4.2 × 1.8 km. Median distance to mapped trace 224 m; 68.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-185 · component 128 (near_trace; 539 closed / 493 emitted px)
Centroid 40.4865°N, 119.2536°W; PCA axis azimuth 11.1° clockwise from north, elongation 3.8:1, axes 5.4 × 1.4 km. Median distance to mapped trace 500 m; 28.8% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median), gravity-gradient/density boundary (grav_hgm, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-186 · component 281 (near_trace; 533 closed / 482 emitted px)
Centroid 40.2453°N, 119.1974°W; PCA axis azimuth 38.6° clockwise from north, elongation 2.5:1, axes 4.8 × 1.9 km. Median distance to mapped trace 316 m; 47.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-187 · component 893 (near_trace; 526 closed / 438 emitted px)
Centroid 38.0249°N, 117.6825°W; PCA axis azimuth 18.3° clockwise from north, elongation 2.1:1, axes 4.0 × 1.9 km. Median distance to mapped trace 224 m; 63.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-188 · component 791 (near_trace; 523 closed / 427 emitted px)
Centroid 38.8080°N, 118.0550°W; PCA axis azimuth 64.6° clockwise from north, elongation 1.7:1, axes 3.9 × 2.3 km. Median distance to mapped trace 781 m; 19.2% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 2.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-189 · component 263 (isolated; 522 closed / 475 emitted px)
Centroid 40.2641°N, 119.3849°W; PCA axis azimuth 177.7° clockwise from north, elongation 3.0:1, axes 5.2 × 1.8 km. Median distance to mapped trace 3828 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-190 · component 29 (isolated; 516 closed / 458 emitted px)
Centroid 40.6931°N, 117.4699°W; PCA axis azimuth 12.8° clockwise from north, elongation 2.7:1, axes 5.5 × 2.0 km. Median distance to mapped trace 1917 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-191 · component 730 (near_trace; 511 closed / 392 emitted px)
Centroid 39.1149°N, 118.8738°W; PCA axis azimuth 1.9° clockwise from north, elongation 1.5:1, axes 3.6 × 2.5 km. Median distance to mapped trace 300 m; 58.7% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 2.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-192 · component 40 (near_trace; 506 closed / 447 emitted px)
Centroid 40.6685°N, 118.0577°W; PCA axis azimuth 4.0° clockwise from north, elongation 1.6:1, axes 3.8 × 2.3 km. Median distance to mapped trace 412 m; 36.9% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.98 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.07 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 2.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-193 · component 124 (isolated; 505 closed / 458 emitted px)
Centroid 40.5158°N, 117.6398°W; PCA axis azimuth 156.8° clockwise from north, elongation 2.3:1, axes 5.1 × 2.2 km. Median distance to mapped trace 2194 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-194 · component 611 (near_trace; 505 closed / 476 emitted px)
Centroid 39.4925°N, 118.0920°W; PCA axis azimuth 7.2° clockwise from north, elongation 1.8:1, axes 3.5 × 1.9 km. Median distance to mapped trace 877 m; 12.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-195 · component 487 (isolated; 504 closed / 463 emitted px)
Centroid 39.8822°N, 118.7203°W; PCA axis azimuth 109.9° clockwise from north, elongation 1.1:1, axes 3.1 × 2.7 km. Median distance to mapped trace 3640 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 2.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-196 · component 921 (near_trace; 501 closed / 391 emitted px)
Centroid 37.8677°N, 117.5821°W; PCA axis azimuth 111.0° clockwise from north, elongation 1.7:1, axes 4.1 × 2.4 km. Median distance to mapped trace 300 m; 51.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-197 · component 81 (near_trace; 493 closed / 430 emitted px)
Centroid 40.6157°N, 118.5144°W; PCA axis azimuth 97.7° clockwise from north, elongation 2.0:1, axes 3.6 × 1.8 km. Median distance to mapped trace 224 m; 71.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-198 · component 614 (isolated; 489 closed / 423 emitted px)
Centroid 39.4718°N, 119.0775°W; PCA axis azimuth 20.7° clockwise from north, elongation 2.8:1, axes 4.8 × 1.7 km. Median distance to mapped trace 1300 m; 0.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-199 · component 849 (near_trace; 488 closed / 409 emitted px)
Centroid 38.4955°N, 118.2167°W; PCA axis azimuth 95.5° clockwise from north, elongation 2.4:1, axes 4.0 × 1.7 km. Median distance to mapped trace 300 m; 54.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.99 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-200 · component 529 (near_trace; 486 closed / 383 emitted px)
Centroid 39.7500°N, 119.5818°W; PCA axis azimuth 139.9° clockwise from north, elongation 1.9:1, axes 4.4 × 2.4 km. Median distance to mapped trace 600 m; 24.5% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-201 · component 199 (isolated; 485 closed / 453 emitted px)
Centroid 40.3695°N, 117.6961°W; PCA axis azimuth 13.0° clockwise from north, elongation 4.8:1, axes 5.8 × 1.2 km. Median distance to mapped trace 7962 m; 0.0% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-202 · component 1 (isolated; 480 closed / 461 emitted px)
Centroid 40.6819°N, 119.2590°W; PCA axis azimuth 37.6° clockwise from north, elongation 6.5:1, axes 6.9 × 1.1 km. Median distance to mapped trace 4000 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-203 · component 16 (near_trace; 480 closed / 418 emitted px)
Centroid 40.7097°N, 117.3859°W; PCA axis azimuth 52.2° clockwise from north, elongation 5.3:1, axes 6.2 × 1.2 km. Median distance to mapped trace 224 m; 65.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-204 · component 170 (isolated; 479 closed / 448 emitted px)
Centroid 40.4082°N, 119.3429°W; PCA axis azimuth 7.7° clockwise from north, elongation 4.5:1, axes 6.1 × 1.3 km. Median distance to mapped trace 2550 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-205 · component 703 (near_trace; 478 closed / 364 emitted px)
Centroid 39.1828°N, 119.1176°W; PCA axis azimuth 18.9° clockwise from north, elongation 2.7:1, axes 5.0 × 1.9 km. Median distance to mapped trace 600 m; 32.4% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.95 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-206 · component 744 (near_trace; 476 closed / 411 emitted px)
Centroid 39.0497°N, 118.2192°W; PCA axis azimuth 32.8° clockwise from north, elongation 2.3:1, axes 4.1 × 1.8 km. Median distance to mapped trace 283 m; 59.1% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.91 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-207 · component 639 (halo; 475 closed / 380 emitted px)
Centroid 39.4114°N, 118.4287°W; PCA axis azimuth 166.2° clockwise from north, elongation 1.5:1, axes 3.5 × 2.4 km. Median distance to mapped trace 200 m; 77.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-208 · component 682 (near_trace; 475 closed / 422 emitted px)
Centroid 39.2424°N, 119.2063°W; PCA axis azimuth 133.3° clockwise from north, elongation 1.5:1, axes 3.2 × 2.1 km. Median distance to mapped trace 224 m; 61.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-209 · component 779 (near_trace; 474 closed / 414 emitted px)
Centroid 38.8442°N, 118.1327°W; PCA axis azimuth 15.4° clockwise from north, elongation 2.9:1, axes 4.4 × 1.5 km. Median distance to mapped trace 200 m; 71.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.91 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.92 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-210 · component 161 (isolated; 468 closed / 427 emitted px)
Centroid 40.4326°N, 118.3134°W; PCA axis azimuth 6.7° clockwise from north, elongation 6.0:1, axes 7.0 × 1.2 km. Median distance to mapped trace 2484 m; 0.0% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.09 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-211 · component 350 (near_trace; 467 closed / 403 emitted px)
Centroid 40.1540°N, 119.6839°W; PCA axis azimuth 174.1° clockwise from north, elongation 2.2:1, axes 3.9 × 1.7 km. Median distance to mapped trace 224 m; 68.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-212 · component 513 (near_trace; 467 closed / 399 emitted px)
Centroid 39.8131°N, 118.8225°W; PCA axis azimuth 98.6° clockwise from north, elongation 1.4:1, axes 2.9 × 2.1 km. Median distance to mapped trace 224 m; 72.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-213 · component 305 (isolated; 465 closed / 434 emitted px)
Centroid 40.2364°N, 116.9753°W; PCA axis azimuth 4.8° clockwise from north, elongation 4.9:1, axes 5.7 × 1.2 km. Median distance to mapped trace 6050 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-214 · component 940 (halo; 453 closed / 372 emitted px)
Centroid 37.7411°N, 117.8183°W; PCA axis azimuth 26.8° clockwise from north, elongation 5.1:1, axes 6.5 × 1.3 km. Median distance to mapped trace 200 m; 79.8% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-215 · component 469 (near_trace; 435 closed / 412 emitted px)
Centroid 39.9203°N, 119.3262°W; PCA axis azimuth 44.4° clockwise from north, elongation 5.3:1, axes 6.2 × 1.2 km. Median distance to mapped trace 2257 m; 10.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-216 · component 13 (near_trace; 429 closed / 402 emitted px)
Centroid 40.7100°N, 117.5233°W; PCA axis azimuth 27.2° clockwise from north, elongation 2.7:1, axes 4.0 × 1.5 km. Median distance to mapped trace 400 m; 39.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-217 · component 823 (near_trace; 424 closed / 368 emitted px)
Centroid 38.6788°N, 118.1864°W; PCA axis azimuth 137.8° clockwise from north, elongation 2.5:1, axes 4.6 × 1.8 km. Median distance to mapped trace 283 m; 53.5% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.93 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.96 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-218 · component 840 (isolated; 420 closed / 368 emitted px)
Centroid 38.5767°N, 118.1228°W; PCA axis azimuth 0.9° clockwise from north, elongation 1.6:1, axes 3.7 × 2.3 km. Median distance to mapped trace 2762 m; 0.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.97 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.96 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 2.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-219 · component 352 (near_trace; 418 closed / 354 emitted px)
Centroid 40.1702°N, 118.6759°W; PCA axis azimuth 30.5° clockwise from north, elongation 2.0:1, axes 3.9 × 2.0 km. Median distance to mapped trace 361 m; 41.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.90 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.01 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-220 · component 560 (isolated; 411 closed / 366 emitted px)
Centroid 39.6211°N, 118.0136°W; PCA axis azimuth 25.7° clockwise from north, elongation 2.0:1, axes 3.9 × 1.9 km. Median distance to mapped trace 3201 m; 0.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.95 regional percentile of the component median), gravity-gradient/density boundary (grav_hgm, high 0.98 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-221 · component 566 (halo; 407 closed / 325 emitted px)
Centroid 39.5916°N, 119.4933°W; PCA axis azimuth 69.7° clockwise from north, elongation 3.8:1, axes 4.8 × 1.3 km. Median distance to mapped trace 200 m; 80.6% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-222 · component 403 (near_trace; 402 closed / 369 emitted px)
Centroid 40.0984°N, 117.9315°W; PCA axis azimuth 46.3° clockwise from north, elongation 4.2:1, axes 5.4 × 1.3 km. Median distance to mapped trace 361 m; 45.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-223 · component 829 (near_trace; 398 closed / 343 emitted px)
Centroid 38.6560°N, 118.2998°W; PCA axis azimuth 118.5° clockwise from north, elongation 2.8:1, axes 4.3 × 1.6 km. Median distance to mapped trace 412 m; 40.2% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.96 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-224 · component 22 (near_trace; 397 closed / 348 emitted px)
Centroid 40.7070°N, 116.2542°W; PCA axis azimuth 14.1° clockwise from north, elongation 2.9:1, axes 4.3 × 1.5 km. Median distance to mapped trace 300 m; 51.1% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.02 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-225 · component 146 (near_trace; 389 closed / 337 emitted px)
Centroid 40.4576°N, 119.2125°W; PCA axis azimuth 153.8° clockwise from north, elongation 2.0:1, axes 4.0 × 2.0 km. Median distance to mapped trace 224 m; 67.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-226 · component 47 (isolated; 382 closed / 361 emitted px)
Centroid 40.6578°N, 116.1660°W; PCA axis azimuth 23.9° clockwise from north, elongation 3.9:1, axes 4.9 × 1.3 km. Median distance to mapped trace 6537 m; 0.0% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.02 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-227 · component 889 (near_trace; 372 closed / 306 emitted px)
Centroid 38.0452°N, 118.0941°W; PCA axis azimuth 87.1° clockwise from north, elongation 2.4:1, axes 4.4 × 1.9 km. Median distance to mapped trace 500 m; 35.3% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.92 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-228 · component 274 (isolated; 368 closed / 339 emitted px)
Centroid 40.2763°N, 117.3952°W; PCA axis azimuth 14.6° clockwise from north, elongation 3.9:1, axes 5.2 × 1.3 km. Median distance to mapped trace 3700 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-229 · component 105 (near_trace; 366 closed / 311 emitted px)
Centroid 40.5634°N, 117.0709°W; PCA axis azimuth 21.8° clockwise from north, elongation 1.5:1, axes 2.8 × 1.9 km. Median distance to mapped trace 300 m; 50.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-230 · component 393 (near_trace; 366 closed / 316 emitted px)
Centroid 40.1256°N, 117.6549°W; PCA axis azimuth 36.0° clockwise from north, elongation 2.5:1, axes 4.8 × 1.9 km. Median distance to mapped trace 914 m; 37.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-231 · component 484 (isolated; 363 closed / 334 emitted px)
Centroid 39.8864°N, 119.5238°W; PCA axis azimuth 131.6° clockwise from north, elongation 4.4:1, axes 4.9 × 1.1 km. Median distance to mapped trace 7962 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-232 · component 404 (near_trace; 361 closed / 318 emitted px)
Centroid 40.0968°N, 117.4528°W; PCA axis azimuth 1.2° clockwise from north, elongation 4.9:1, axes 5.4 × 1.1 km. Median distance to mapped trace 316 m; 49.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-233 · component 688 (near_trace; 358 closed / 304 emitted px)
Centroid 39.2140°N, 119.2807°W; PCA axis azimuth 177.0° clockwise from north, elongation 2.0:1, axes 3.2 × 1.6 km. Median distance to mapped trace 283 m; 59.2% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-234 · component 609 (near_trace; 353 closed / 308 emitted px)
Centroid 39.4848°N, 119.3441°W; PCA axis azimuth 78.4° clockwise from north, elongation 1.9:1, axes 3.0 × 1.6 km. Median distance to mapped trace 224 m; 64.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-235 · component 409 (near_trace; 352 closed / 290 emitted px)
Centroid 40.0961°N, 117.3895°W; PCA axis azimuth 97.4° clockwise from north, elongation 2.6:1, axes 4.4 × 1.7 km. Median distance to mapped trace 400 m; 41.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-236 · component 734 (near_trace; 350 closed / 310 emitted px)
Centroid 39.1001°N, 119.0041°W; PCA axis azimuth 172.8° clockwise from north, elongation 2.3:1, axes 3.9 × 1.7 km. Median distance to mapped trace 707 m; 32.9% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.98 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.94 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-237 · component 883 (near_trace; 344 closed / 305 emitted px)
Centroid 38.0941°N, 117.8473°W; PCA axis azimuth 155.1° clockwise from north, elongation 4.3:1, axes 4.9 × 1.1 km. Median distance to mapped trace 224 m; 72.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-238 · component 630 (near_trace; 342 closed / 273 emitted px)
Centroid 39.4342°N, 118.6116°W; PCA axis azimuth 90.7° clockwise from north, elongation 1.3:1, axes 2.6 × 2.0 km. Median distance to mapped trace 283 m; 62.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 2.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-239 · component 905 (near_trace; 340 closed / 301 emitted px)
Centroid 37.9595°N, 118.3637°W; PCA axis azimuth 73.5° clockwise from north, elongation 1.9:1, axes 2.9 × 1.6 km. Median distance to mapped trace 316 m; 43.9% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.97 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.99 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-240 · component 346 (near_trace; 339 closed / 275 emitted px)
Centroid 40.1955°N, 117.3113°W; PCA axis azimuth 93.1° clockwise from north, elongation 1.8:1, axes 4.3 × 2.4 km. Median distance to mapped trace 224 m; 62.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 2.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-241 · component 565 (near_trace; 339 closed / 267 emitted px)
Centroid 39.5939°N, 119.3396°W; PCA axis azimuth 21.2° clockwise from north, elongation 1.6:1, axes 3.5 × 2.3 km. Median distance to mapped trace 900 m; 27.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 2.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-242 · component 456 (isolated; 338 closed / 314 emitted px)
Centroid 39.9978°N, 118.5053°W; PCA axis azimuth 57.9° clockwise from north, elongation 3.5:1, axes 4.4 × 1.3 km. Median distance to mapped trace 7608 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-243 · component 500 (near_trace; 338 closed / 280 emitted px)
Centroid 39.8300°N, 119.8208°W; PCA axis azimuth 54.9° clockwise from north, elongation 5.3:1, axes 5.5 × 1.0 km. Median distance to mapped trace 316 m; 47.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-244 · component 638 (halo; 336 closed / 280 emitted px)
Centroid 39.4021°N, 118.8327°W; PCA axis azimuth 8.9° clockwise from north, elongation 5.5:1, axes 5.1 × 0.9 km. Median distance to mapped trace 200 m; 83.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-245 · component 54 (near_trace; 335 closed / 313 emitted px)
Centroid 40.6357°N, 119.2278°W; PCA axis azimuth 40.5° clockwise from north, elongation 2.3:1, axes 3.2 × 1.4 km. Median distance to mapped trace 640 m; 26.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-246 · component 473 (near_trace; 335 closed / 289 emitted px)
Centroid 39.9009°N, 119.8705°W; PCA axis azimuth 123.4° clockwise from north, elongation 3.9:1, axes 4.8 × 1.2 km. Median distance to mapped trace 400 m; 42.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-247 · component 134 (near_trace; 333 closed / 310 emitted px)
Centroid 40.5000°N, 117.9665°W; PCA axis azimuth 154.2° clockwise from north, elongation 2.5:1, axes 3.4 × 1.4 km. Median distance to mapped trace 500 m; 32.9% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-248 · component 247 (isolated; 332 closed / 306 emitted px)
Centroid 40.2862°N, 119.2740°W; PCA axis azimuth 176.2° clockwise from north, elongation 4.3:1, axes 4.4 × 1.0 km. Median distance to mapped trace 1221 m; 6.2% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-249 · component 429 (near_trace; 331 closed / 275 emitted px)
Centroid 40.0597°N, 117.4878°W; PCA axis azimuth 175.6° clockwise from north, elongation 4.0:1, axes 4.5 × 1.1 km. Median distance to mapped trace 283 m; 60.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-250 · component 918 (near_trace; 327 closed / 270 emitted px)
Centroid 37.8890°N, 117.6562°W; PCA axis azimuth 27.8° clockwise from north, elongation 1.7:1, axes 3.8 × 2.2 km. Median distance to mapped trace 200 m; 73.3% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 2.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-251 · component 794 (near_trace; 326 closed / 291 emitted px)
Centroid 38.8032°N, 118.2645°W; PCA axis azimuth 27.0° clockwise from north, elongation 1.4:1, axes 2.5 × 1.8 km. Median distance to mapped trace 300 m; 61.5% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.94 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.95 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-252 · component 99 (isolated; 324 closed / 311 emitted px)
Centroid 40.5814°N, 116.5155°W; PCA axis azimuth 61.2° clockwise from north, elongation 5.0:1, axes 4.8 × 1.0 km. Median distance to mapped trace 6037 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-253 · component 593 (near_trace; 323 closed / 264 emitted px)
Centroid 39.5238°N, 119.3768°W; PCA axis azimuth 167.5° clockwise from north, elongation 2.2:1, axes 3.8 × 1.7 km. Median distance to mapped trace 224 m; 62.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-254 · component 100 (isolated; 322 closed / 280 emitted px)
Centroid 40.5537°N, 119.0303°W; PCA axis azimuth 5.9° clockwise from north, elongation 4.5:1, axes 4.9 × 1.1 km. Median distance to mapped trace 2766 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-255 · component 780 (near_trace; 322 closed / 286 emitted px)
Centroid 38.8467°N, 118.4024°W; PCA axis azimuth 127.5° clockwise from north, elongation 1.3:1, axes 2.4 × 1.8 km. Median distance to mapped trace 224 m; 60.1% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.93 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.91 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-256 · component 435 (near_trace; 321 closed / 279 emitted px)
Centroid 40.0587°N, 117.5077°W; PCA axis azimuth 174.4° clockwise from north, elongation 3.4:1, axes 3.8 × 1.1 km. Median distance to mapped trace 412 m; 38.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-257 · component 133 (isolated; 320 closed / 304 emitted px)
Centroid 40.4987°N, 116.2211°W; PCA axis azimuth 12.0° clockwise from north, elongation 5.3:1, axes 4.8 × 0.9 km. Median distance to mapped trace 2151 m; 0.0% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.03 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-258 · component 709 (near_trace; 317 closed / 280 emitted px)
Centroid 39.1765°N, 118.4761°W; PCA axis azimuth 26.5° clockwise from north, elongation 3.0:1, axes 4.6 × 1.6 km. Median distance to mapped trace 1556 m; 20.4% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.91 regional percentile of the component median), magnetic gradient/contact (mag_hgm, high 0.95 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.91 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.97 regional percentile of the component median) (4/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (3.0:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-259 · component 211 (halo; 314 closed / 267 emitted px)
Centroid 40.3590°N, 118.1117°W; PCA axis azimuth 159.2° clockwise from north, elongation 3.9:1, axes 4.1 × 1.1 km. Median distance to mapped trace 200 m; 75.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-260 · component 176 (near_trace; 313 closed / 290 emitted px)
Centroid 40.4227°N, 117.2417°W; PCA axis azimuth 28.7° clockwise from north, elongation 4.6:1, axes 4.5 × 1.0 km. Median distance to mapped trace 316 m; 49.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-261 · component 195 (near_trace; 313 closed / 257 emitted px)
Centroid 40.3929°N, 116.7478°W; PCA axis azimuth 137.1° clockwise from north, elongation 1.8:1, axes 3.2 × 1.7 km. Median distance to mapped trace 806 m; 42.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-262 · component 934 (isolated; 311 closed / 267 emitted px)
Centroid 37.7809°N, 117.6496°W; PCA axis azimuth 128.3° clockwise from north, elongation 2.6:1, axes 4.8 × 1.8 km. Median distance to mapped trace 7106 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-263 · component 330 (near_trace; 309 closed / 282 emitted px)
Centroid 40.2047°N, 117.2291°W; PCA axis azimuth 20.2° clockwise from north, elongation 3.9:1, axes 4.1 × 1.0 km. Median distance to mapped trace 316 m; 49.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-264 · component 676 (isolated; 304 closed / 285 emitted px)
Centroid 39.2749°N, 118.7216°W; PCA axis azimuth 79.2° clockwise from north, elongation 2.8:1, axes 3.8 × 1.4 km. Median distance to mapped trace 2209 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.8:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-265 · component 501 (near_trace; 303 closed / 255 emitted px)
Centroid 39.8574°N, 118.2649°W; PCA axis azimuth 140.4° clockwise from north, elongation 2.1:1, axes 2.9 × 1.4 km. Median distance to mapped trace 283 m; 58.4% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 1.00 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-266 · component 644 (halo; 303 closed / 254 emitted px)
Centroid 39.4027°N, 118.6063°W; PCA axis azimuth 68.4° clockwise from north, elongation 1.1:1, axes 2.1 × 1.9 km. Median distance to mapped trace 171 m; 77.6% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median), magnetic gradient/contact (mag_hgm, high 0.91 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-267 · component 319 (isolated; 299 closed / 253 emitted px)
Centroid 40.2297°N, 117.5607°W; PCA axis azimuth 97.7° clockwise from north, elongation 1.6:1, axes 3.2 × 2.1 km. Median distance to mapped trace 4327 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-268 · component 320 (near_trace; 296 closed / 238 emitted px)
Centroid 40.2282°N, 116.1913°W; PCA axis azimuth 47.1° clockwise from north, elongation 1.6:1, axes 2.6 × 1.6 km. Median distance to mapped trace 224 m; 58.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-269 · component 603 (near_trace; 296 closed / 243 emitted px)
Centroid 39.5050°N, 118.9843°W; PCA axis azimuth 95.1° clockwise from north, elongation 1.5:1, axes 2.7 × 1.8 km. Median distance to mapped trace 283 m; 56.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-270 · component 108 (isolated; 293 closed / 240 emitted px)
Centroid 40.5562°N, 117.1535°W; PCA axis azimuth 145.3° clockwise from north, elongation 2.3:1, axes 3.9 × 1.7 km. Median distance to mapped trace 5654 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-271 · component 649 (near_trace; 293 closed / 261 emitted px)
Centroid 39.3857°N, 118.4630°W; PCA axis azimuth 18.0° clockwise from north, elongation 2.7:1, axes 3.3 × 1.2 km. Median distance to mapped trace 224 m; 60.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-272 · component 814 (isolated; 293 closed / 280 emitted px)
Centroid 38.7064°N, 118.3778°W; PCA axis azimuth 176.3° clockwise from north, elongation 2.9:1, axes 3.4 × 1.2 km. Median distance to mapped trace 1972 m; 0.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.91 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.96 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-273 · component 571 (near_trace; 292 closed / 221 emitted px)
Centroid 39.5954°N, 118.7982°W; PCA axis azimuth 23.7° clockwise from north, elongation 1.2:1, axes 2.5 × 2.1 km. Median distance to mapped trace 200 m; 69.7% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.2:1; minor axis 2.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-274 · component 890 (near_trace; 291 closed / 268 emitted px)
Centroid 38.0459°N, 117.4308°W; PCA axis azimuth 148.0° clockwise from north, elongation 2.7:1, axes 3.6 × 1.3 km. Median distance to mapped trace 825 m; 10.4% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-275 · component 894 (halo; 291 closed / 244 emitted px)
Centroid 38.0197°N, 117.4580°W; PCA axis azimuth 169.7° clockwise from north, elongation 3.4:1, axes 3.7 × 1.1 km. Median distance to mapped trace 200 m; 75.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-276 · component 139 (near_trace; 290 closed / 270 emitted px)
Centroid 40.5026°N, 116.6684°W; PCA axis azimuth 73.6° clockwise from north, elongation 4.0:1, axes 3.9 × 1.0 km. Median distance to mapped trace 791 m; 26.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-277 · component 448 (isolated; 288 closed / 276 emitted px)
Centroid 40.0119°N, 119.3855°W; PCA axis azimuth 158.9° clockwise from north, elongation 2.1:1, axes 3.1 × 1.4 km. Median distance to mapped trace 7329 m; 0.0% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-278 · component 702 (near_trace; 285 closed / 254 emitted px)
Centroid 39.2100°N, 118.0390°W; PCA axis azimuth 163.0° clockwise from north, elongation 1.3:1, axes 2.2 × 1.7 km. Median distance to mapped trace 224 m; 74.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.99 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.96 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 1.7 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-279 · component 502 (isolated; 284 closed / 276 emitted px)
Centroid 39.8289°N, 119.6385°W; PCA axis azimuth 153.1° clockwise from north, elongation 3.0:1, axes 3.4 × 1.1 km. Median distance to mapped trace 2720 m; 0.0% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.91 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-280 · component 337 (near_trace; 283 closed / 221 emitted px)
Centroid 40.2022°N, 117.1034°W; PCA axis azimuth 179.4° clockwise from north, elongation 2.5:1, axes 4.0 × 1.6 km. Median distance to mapped trace 224 m; 68.8% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-281 · component 74 (isolated; 280 closed / 272 emitted px)
Centroid 40.6249°N, 117.3985°W; PCA axis azimuth 133.0° clockwise from north, elongation 3.7:1, axes 4.1 × 1.1 km. Median distance to mapped trace 1701 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-282 · component 196 (near_trace; 277 closed / 240 emitted px)
Centroid 40.3767°N, 118.7281°W; PCA axis azimuth 21.9° clockwise from north, elongation 2.0:1, axes 2.9 × 1.5 km. Median distance to mapped trace 283 m; 55.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-283 · component 685 (isolated; 274 closed / 252 emitted px)
Centroid 39.2552°N, 118.0269°W; PCA axis azimuth 2.1° clockwise from north, elongation 2.4:1, axes 3.0 × 1.2 km. Median distance to mapped trace 2400 m; 0.0% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-284 · component 615 (halo; 273 closed / 224 emitted px)
Centroid 39.4851°N, 119.0407°W; PCA axis azimuth 51.9° clockwise from north, elongation 3.2:1, axes 3.5 × 1.1 km. Median distance to mapped trace 141 m; 89.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-285 · component 670 (near_trace; 272 closed / 216 emitted px)
Centroid 39.2768°N, 119.3824°W; PCA axis azimuth 40.2° clockwise from north, elongation 2.6:1, axes 3.9 × 1.5 km. Median distance to mapped trace 316 m; 48.1% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.91 regional percentile of the component median), geodetic shear rate (geod_shearrate, high 0.91 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.6:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-286 · component 276 (near_trace; 271 closed / 196 emitted px)
Centroid 40.2739°N, 118.2409°W; PCA axis azimuth 120.1° clockwise from north, elongation 3.0:1, axes 3.9 × 1.3 km. Median distance to mapped trace 500 m; 32.7% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-287 · component 264 (near_trace; 268 closed / 219 emitted px)
Centroid 40.2944°N, 117.8730°W; PCA axis azimuth 38.0° clockwise from north, elongation 2.9:1, axes 3.6 × 1.2 km. Median distance to mapped trace 500 m; 26.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-288 · component 246 (near_trace; 267 closed / 241 emitted px)
Centroid 40.2895°N, 119.4635°W; PCA axis azimuth 36.6° clockwise from north, elongation 2.7:1, axes 3.1 × 1.1 km. Median distance to mapped trace 224 m; 65.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-289 · component 460 (near_trace; 265 closed / 207 emitted px)
Centroid 39.9839°N, 118.8446°W; PCA axis azimuth 20.0° clockwise from north, elongation 2.0:1, axes 2.7 × 1.4 km. Median distance to mapped trace 283 m; 56.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-290 · component 726 (near_trace; 265 closed / 230 emitted px)
Centroid 39.1231°N, 118.8116°W; PCA axis azimuth 172.7° clockwise from north, elongation 2.2:1, axes 2.8 × 1.3 km. Median distance to mapped trace 316 m; 47.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-291 · component 793 (near_trace; 265 closed / 237 emitted px)
Centroid 38.7974°N, 118.5223°W; PCA axis azimuth 173.0° clockwise from north, elongation 2.9:1, axes 3.3 × 1.1 km. Median distance to mapped trace 224 m; 67.5% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.9:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-292 · component 798 (near_trace; 264 closed / 229 emitted px)
Centroid 38.7943°N, 117.9776°W; PCA axis azimuth 21.8° clockwise from north, elongation 2.2:1, axes 2.8 × 1.3 km. Median distance to mapped trace 224 m; 62.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.2:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-293 · component 89 (near_trace; 263 closed / 214 emitted px)
Centroid 40.6026°N, 117.3369°W; PCA axis azimuth 156.1° clockwise from north, elongation 1.3:1, axes 2.6 × 1.9 km. Median distance to mapped trace 283 m; 55.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 1.9 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-294 · component 598 (near_trace; 260 closed / 214 emitted px)
Centroid 39.5151°N, 119.1276°W; PCA axis azimuth 106.3° clockwise from north, elongation 2.3:1, axes 3.0 × 1.3 km. Median distance to mapped trace 224 m; 62.6% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.3:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-295 · component 140 (isolated; 259 closed / 231 emitted px)
Centroid 40.4893°N, 116.3026°W; PCA axis azimuth 2.2° clockwise from north, elongation 3.3:1, axes 3.7 × 1.1 km. Median distance to mapped trace 4528 m; 0.0% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.05 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-296 · component 310 (isolated; 259 closed / 236 emitted px)
Centroid 40.2323°N, 118.0756°W; PCA axis azimuth 24.7° clockwise from north, elongation 2.4:1, axes 3.0 × 1.3 km. Median distance to mapped trace 6364 m; 0.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.97 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-297 · component 44 (isolated; 258 closed / 247 emitted px)
Centroid 40.6698°N, 117.0710°W; PCA axis azimuth 11.4° clockwise from north, elongation 2.4:1, axes 3.1 × 1.3 km. Median distance to mapped trace 5661 m; 0.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-298 · component 665 (halo; 258 closed / 217 emitted px)
Centroid 39.3203°N, 119.0394°W; PCA axis azimuth 104.3° clockwise from north, elongation 1.8:1, axes 2.5 × 1.4 km. Median distance to mapped trace 200 m; 83.9% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.93 regional percentile of the component median), geodetic shear rate (geod_shearrate, high 0.91 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-299 · component 684 (near_trace; 257 closed / 226 emitted px)
Centroid 39.2601°N, 118.0791°W; PCA axis azimuth 73.6° clockwise from north, elongation 1.3:1, axes 2.1 × 1.6 km. Median distance to mapped trace 224 m; 69.0% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.98 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-300 · component 756 (near_trace; 257 closed / 246 emitted px)
Centroid 39.0099°N, 118.6066°W; PCA axis azimuth 143.6° clockwise from north, elongation 4.9:1, axes 4.1 × 0.8 km. Median distance to mapped trace 412 m; 35.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-301 · component 411 (near_trace; 256 closed / 203 emitted px)
Centroid 40.0949°N, 117.4833°W; PCA axis azimuth 77.1° clockwise from north, elongation 1.1:1, axes 2.0 × 1.8 km. Median distance to mapped trace 400 m; 49.8% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-302 · component 104 (isolated; 253 closed / 245 emitted px)
Centroid 40.5682°N, 117.7584°W; PCA axis azimuth 45.5° clockwise from north, elongation 3.0:1, axes 3.2 × 1.1 km. Median distance to mapped trace 7741 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (3.0:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-303 · component 755 (isolated; 253 closed / 237 emitted px)
Centroid 39.0194°N, 118.5698°W; PCA axis azimuth 167.0° clockwise from north, elongation 2.1:1, axes 3.0 × 1.4 km. Median distance to mapped trace 2640 m; 0.0% within 300 m.
**Measured support:** geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-304 · component 944 (near_trace; 253 closed / 221 emitted px)
Centroid 37.7078°N, 118.0312°W; PCA axis azimuth 4.0° clockwise from north, elongation 1.9:1, axes 2.5 × 1.4 km. Median distance to mapped trace 283 m; 58.8% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.94 regional percentile of the component median), gravity-gradient/density boundary (grav_hgm, high 0.93 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.99 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.4 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-305 · component 351 (near_trace; 252 closed / 219 emitted px)
Centroid 40.1878°N, 117.0846°W; PCA axis azimuth 12.6° clockwise from north, elongation 2.7:1, axes 3.0 × 1.1 km. Median distance to mapped trace 283 m; 61.2% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-306 · component 12 (isolated; 251 closed / 232 emitted px)
Centroid 40.7152°N, 117.5813°W; PCA axis azimuth 24.9° clockwise from north, elongation 2.1:1, axes 2.7 × 1.3 km. Median distance to mapped trace 4783 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.1:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-307 · component 766 (near_trace; 251 closed / 223 emitted px)
Centroid 38.9080°N, 118.4705°W; PCA axis azimuth 150.0° clockwise from north, elongation 2.4:1, axes 3.0 × 1.3 km. Median distance to mapped trace 412 m; 38.1% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.96 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.94 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-308 · component 62 (near_trace; 250 closed / 231 emitted px)
Centroid 40.6432°N, 116.4394°W; PCA axis azimuth 18.9° clockwise from north, elongation 3.5:1, axes 3.4 × 1.0 km. Median distance to mapped trace 300 m; 52.8% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.07 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-309 · component 886 (near_trace; 250 closed / 225 emitted px)
Centroid 38.0747°N, 117.4435°W; PCA axis azimuth 162.5° clockwise from north, elongation 2.0:1, axes 2.6 × 1.3 km. Median distance to mapped trace 316 m; 47.6% within 300 m.
**Measured support:** analytic-signal amplitude of gravity (grav_asa, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-310 · component 434 (isolated; 249 closed / 224 emitted px)
Centroid 40.0648°N, 116.6635°W; PCA axis azimuth 136.3° clockwise from north, elongation 2.0:1, axes 2.9 × 1.5 km. Median distance to mapped trace 2006 m; 0.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.95 regional percentile of the component median), short distance to earthquakes (not the density band) (deq_n100a15, low 0.07 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-311 · component 556 (near_trace; 246 closed / 195 emitted px)
Centroid 39.6542°N, 118.4640°W; PCA axis azimuth 2.4° clockwise from north, elongation 3.5:1, axes 3.5 × 1.0 km. Median distance to mapped trace 200 m; 74.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-312 · component 18 (near_trace; 245 closed / 211 emitted px)
Centroid 40.7178°N, 116.6164°W; PCA axis azimuth 35.9° clockwise from north, elongation 1.6:1, axes 2.4 × 1.5 km. Median distance to mapped trace 224 m; 64.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-313 · component 417 (isolated; 242 closed / 228 emitted px)
Centroid 40.0839°N, 117.2674°W; PCA axis azimuth 50.7° clockwise from north, elongation 4.2:1, axes 4.2 × 1.0 km. Median distance to mapped trace 3106 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-314 · component 719 (isolated; 242 closed / 218 emitted px)
Centroid 39.1581°N, 118.1944°W; PCA axis azimuth 139.4° clockwise from north, elongation 3.6:1, axes 3.9 × 1.1 km. Median distance to mapped trace 2202 m; 0.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.91 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.94 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.92 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** provisional moderate as a target for expert checking. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-315 · component 748 (near_trace; 242 closed / 212 emitted px)
Centroid 39.0434°N, 118.6559°W; PCA axis azimuth 173.7° clockwise from north, elongation 1.4:1, axes 2.1 × 1.6 km. Median distance to mapped trace 849 m; 16.5% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-316 · component 946 (near_trace; 242 closed / 199 emitted px)
Centroid 37.7024°N, 117.6546°W; PCA axis azimuth 33.6° clockwise from north, elongation 1.8:1, axes 2.4 × 1.3 km. Median distance to mapped trace 200 m; 72.9% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-317 · component 900 (near_trace; 241 closed / 199 emitted px)
Centroid 37.9973°N, 117.9032°W; PCA axis azimuth 117.4° clockwise from north, elongation 1.7:1, axes 2.6 × 1.6 km. Median distance to mapped trace 707 m; 29.1% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.7:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-318 · component 542 (isolated; 239 closed / 216 emitted px)
Centroid 39.7175°N, 119.6669°W; PCA axis azimuth 144.5° clockwise from north, elongation 1.6:1, axes 2.5 × 1.6 km. Median distance to mapped trace 1391 m; 0.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.96 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (1.6:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-319 · component 708 (near_trace; 236 closed / 204 emitted px)
Centroid 39.1721°N, 119.2573°W; PCA axis azimuth 105.2° clockwise from north, elongation 1.1:1, axes 2.0 × 1.8 km. Median distance to mapped trace 361 m; 43.1% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.93 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.1:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-320 · component 672 (near_trace; 234 closed / 196 emitted px)
Centroid 39.2977°N, 118.1968°W; PCA axis azimuth 4.6° clockwise from north, elongation 1.5:1, axes 2.2 × 1.5 km. Median distance to mapped trace 200 m; 68.4% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.91 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.94 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.5:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-321 · component 616 (isolated; 230 closed / 194 emitted px)
Centroid 39.4766°N, 119.0114°W; PCA axis azimuth 48.2° clockwise from north, elongation 5.4:1, axes 4.6 × 0.8 km. Median distance to mapped trace 2110 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-322 · component 809 (near_trace; 230 closed / 196 emitted px)
Centroid 38.7259°N, 118.1596°W; PCA axis azimuth 137.1° clockwise from north, elongation 4.1:1, axes 3.8 × 0.9 km. Median distance to mapped trace 283 m; 56.6% within 300 m.
**Measured support:** gravity-gradient/density boundary (grav_hgm, high 0.91 regional percentile of the component median), earthquake-related intensity/density band (ieq_n100a15, high 0.92 regional percentile of the component median), geodetic dilatation rate (geod_dilaterate, high 0.93 regional percentile of the component median) (3/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-323 · component 447 (halo; 227 closed / 199 emitted px)
Centroid 40.0419°N, 116.5674°W; PCA axis azimuth 153.4° clockwise from north, elongation 1.8:1, axes 2.3 × 1.3 km. Median distance to mapped trace 200 m; 81.9% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.93 regional percentile of the component median), gravity-gradient/density boundary (grav_hgm, high 0.99 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (1.8:1; minor axis 1.3 km), not a thin fault trace.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-324 · component 77 (isolated; 222 closed / 210 emitted px)
Centroid 40.6219°N, 117.4930°W; PCA axis azimuth 6.7° clockwise from north, elongation 2.5:1, axes 2.7 × 1.1 km. Median distance to mapped trace 1391 m; 1.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-325 · component 859 (isolated; 222 closed / 175 emitted px)
Centroid 38.4293°N, 118.5581°W; PCA axis azimuth 120.0° clockwise from north, elongation 2.0:1, axes 3.7 × 1.8 km. Median distance to mapped trace 2596 m; 0.0% within 300 m.
**Measured support:** earthquake-related intensity/density band (ieq_n100a15, high 0.99 regional percentile of the component median), regional geodetic strain (geod_2ndinv, high 0.98 regional percentile of the component median) (2/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.8 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-326 · component 93 (near_trace; 219 closed / 189 emitted px)
Centroid 40.5941°N, 117.0603°W; PCA axis azimuth 180.0° clockwise from north, elongation 2.7:1, axes 3.0 × 1.1 km. Median distance to mapped trace 300 m; 55.6% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-327 · component 120 (near_trace; 217 closed / 175 emitted px)
Centroid 40.5364°N, 117.0862°W; PCA axis azimuth 179.7° clockwise from north, elongation 1.4:1, axes 2.1 × 1.6 km. Median distance to mapped trace 361 m; 44.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.4:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-328 · component 678 (near_trace; 216 closed / 190 emitted px)
Centroid 39.2661°N, 118.7712°W; PCA axis azimuth 81.2° clockwise from north, elongation 2.0:1, axes 2.4 × 1.2 km. Median distance to mapped trace 300 m; 56.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-329 · component 869 (halo; 216 closed / 188 emitted px)
Centroid 38.3270°N, 117.8043°W; PCA axis azimuth 147.7° clockwise from north, elongation 2.4:1, axes 2.6 × 1.1 km. Median distance to mapped trace 200 m; 76.1% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-330 · component 800 (near_trace; 214 closed / 198 emitted px)
Centroid 38.7762°N, 118.7510°W; PCA axis azimuth 170.7° clockwise from north, elongation 1.9:1, axes 2.4 × 1.2 km. Median distance to mapped trace 361 m; 44.4% within 300 m.
**Measured support:** regional geodetic strain (geod_2ndinv, high 0.94 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (1.9:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-331 · component 203 (isolated; 213 closed / 188 emitted px)
Centroid 40.3703°N, 118.3251°W; PCA axis azimuth 14.1° clockwise from north, elongation 3.3:1, axes 3.1 × 0.9 km. Median distance to mapped trace 4621 m; 0.0% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.06 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-332 · component 254 (isolated; 213 closed / 205 emitted px)
Centroid 40.3108°N, 117.3130°W; PCA axis azimuth 150.9° clockwise from north, elongation 1.3:1, axes 2.0 × 1.6 km. Median distance to mapped trace 7185 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 1.6 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-333 · component 328 (halo; 213 closed / 185 emitted px)
Centroid 40.2097°N, 117.3702°W; PCA axis azimuth 143.3° clockwise from north, elongation 3.7:1, axes 3.3 × 0.9 km. Median distance to mapped trace 200 m; 77.3% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** very low (no diagnostic family in its favourable regional decile); mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-334 · component 95 (near_trace; 211 closed / 180 emitted px)
Centroid 40.5716°N, 118.9895°W; PCA axis azimuth 30.4° clockwise from north, elongation 4.3:1, axes 3.7 × 0.9 km. Median distance to mapped trace 316 m; 47.8% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.90 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-335 · component 589 (isolated; 210 closed / 190 emitted px)
Centroid 39.5516°N, 118.3781°W; PCA axis azimuth 12.9° clockwise from north, elongation 1.3:1, axes 1.9 × 1.5 km. Median distance to mapped trace 1996 m; 0.0% within 300 m.
**Measured support:** magnetic gradient/contact (mag_hgm, high 0.95 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (1.3:1; minor axis 1.5 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-336 · component 14 (isolated; 208 closed / 176 emitted px)
Centroid 40.7203°N, 117.4322°W; PCA axis azimuth 100.0° clockwise from north, elongation 2.4:1, axes 2.8 × 1.2 km. Median distance to mapped trace 1212 m; 4.5% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.4:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-337 · component 235 (isolated; 208 closed / 199 emitted px)
Centroid 40.3306°N, 117.7228°W; PCA axis azimuth 162.8° clockwise from north, elongation 2.0:1, axes 2.3 × 1.2 km. Median distance to mapped trace 6964 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.0:1; minor axis 1.2 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-338 · component 472 (isolated; 204 closed / 183 emitted px)
Centroid 39.9065°N, 119.9690°W; PCA axis azimuth 104.1° clockwise from north, elongation 3.7:1, axes 3.4 × 0.9 km. Median distance to mapped trace 2062 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-339 · component 680 (halo; 204 closed / 169 emitted px)
Centroid 39.2493°N, 119.1764°W; PCA axis azimuth 124.2° clockwise from north, elongation 3.8:1, axes 3.3 × 0.9 km. Median distance to mapped trace 200 m; 83.4% within 300 m.
**Measured support:** geodetic shear rate (geod_shearrate, high 0.92 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-340 · component 51 (halo; 203 closed / 161 emitted px)
Centroid 40.6602°N, 116.4085°W; PCA axis azimuth 178.3° clockwise from north, elongation 3.3:1, axes 3.2 × 1.0 km. Median distance to mapped trace 200 m; 85.7% within 300 m.
**Measured support:** short distance to earthquakes (not the density band) (deq_n100a15, low 0.04 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** This hugs a known trace and might flag a location correction or an adjacent splay, but no distinct new structure is established.
**Counterinterpretation:** It may only rediscover the mapped fault's surrounding anomaly. The mask excludes the exact mapped pixels, not this surrounding area.
**Assessment:** low as a fault identification; mapped-trace halo dominates. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-341 · component 117 (near_trace; 202 closed / 172 emitted px)
Centroid 40.5373°N, 116.8548°W; PCA axis azimuth 37.0° clockwise from north, elongation 2.5:1, axes 2.7 × 1.1 km. Median distance to mapped trace 224 m; 67.4% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A mapped-trace extension, a nearby splay, or a corrected trace position is possible; distance alone does NOT distinguish them. Such a correction can be new-fault truth under the organizers' pixel-exact known-fault mask.
**Counterinterpretation:** Prediction near a catalogued trace could instead be its geophysical halo with no new fault at all; nearby off-catalogue pixels still pay false-positive cost. Its PCA footprint is broad or weakly elongated (2.5:1; minor axis 1.1 km), not a thin fault trace.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-342 · component 557 (isolated; 201 closed / 196 emitted px)
Centroid 39.6664°N, 117.9875°W; PCA axis azimuth 53.4° clockwise from north, elongation 2.7:1, axes 2.8 × 1.0 km. Median distance to mapped trace 8281 m; 0.0% within 300 m.
**Measured support:** conductivity anomaly (cond_surf, high 0.99 regional percentile of the component median) (1/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault. Its PCA footprint is broad or weakly elongated (2.7:1; minor axis 1.0 km), not a thin fault trace.
**Assessment:** low as a fault identification. Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.

### S-343 · component 250 (isolated; 200 closed / 180 emitted px)
Centroid 40.3109°N, 117.7026°W; PCA axis azimuth 172.5° clockwise from north, elongation 3.1:1, axes 3.2 × 1.0 km. Median distance to mapped trace 4306 m; 0.0% within 300 m.
**Measured support:** No diagnostic family in its fault-favourable regional decile (0/6 diagnostic families.)
**Fault hypothesis:** A lineament spatially separate from the supplied mapped trace could be an unmapped fault if the anomaly tracks a break in geologic structure.
**Counterinterpretation:** A lithological contact or drainage-aligned surface feature could be equally isolated; distance from a map is not proof of a new fault.
**Assessment:** very low (no diagnostic family in its favourable regional decile). Seek 1 m scarp geometry, mapped contact continuity and expert cross-section/field check before calling this a fault; depth unestimated.
