"""Content for the GEMS Prize research knowledge base.

DISCIPLINE OF THIS FILE
Every factual sentence rendered from here must be traceable to one of:
  * a primary official source fetched and read on 2026-09-26 (listed in ANCHORS,
    with the fetch recorded in evidence/gems/), quoted exactly where quoted;
  * this project's own committed measurement evidence (gemsdoe_review/evidence/*.json),
    cited by path and re-checked against the file before publication;
  * the official competition rasters placed and hash-verified by
    scripts/download_competition_data.sh and read by scripts/prepare_data.py.
Anything else is marked UNVERIFIED in the text. Quotes are verbatim; ellipses are
marked. This file is data, not code: tools/build_gems_research.py renders it.
"""

CHECK_DATE = "2026-09-26"

# ---------------------------------------------------------------------------
# Verified anchor register. `status` records what the 2026-09-26 check actually did.
# ---------------------------------------------------------------------------
ANCHORS = [
    {
        "id": "hub",
        "name": "Competition hub (DrivenData)",
        "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/",
        "what": "Live competition page: end date Dec. 3, 2026, 11:59 p.m. UTC; total prize pool $300,000 "
        "($50,000 initial round split five ways, $250,000 final round: $100k/$70k/$40k/$25k/$15k); "
        "how-to-compete steps; eligibility summary; external-data encouragement; sponsor DOE Office of "
        "Geothermal with support from the National Lab of the Rockies (NLR).",
        "key_quote": "The same submission is scored twice — once against a private expert-labeled test set "
        "for the Initial Prize Round, and again against an expanded label set built from expert review of "
        "all submissions for the Final Prize Round.",
        "status": "fetched and read in full, 2026-09-26",
    },
    {
        "id": "problem",
        "name": "Problem description (page/967)",
        "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
        "what": "The authoritative task, dataset, metric and submission-format text: two-round structure; "
        "supplied rasters; the distance-weighted Tversky index with alpha=0.2, beta=0.8 and a 300 m "
        "triangular kernel, with worked example; submission format (EPSG:32611, 100 m, single float32 "
        "band in [0,1], NaN outside the training bounds).",
        "key_quote": "While detailed, it is known that this set of faults is not complete and may even "
        "contain some inaccurate data.",
        "status": "fetched and read in full (2 chunks), 2026-09-26",
    },
    {
        "id": "about",
        "name": "About / resources (page/968)",
        "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/",
        "what": "Sponsor and data background (GeoDAWN under EarthMRI with 3DEP lidar; DOE Office of "
        "Geothermal), an orientation to fault detection methods, and two officially cited prior-art "
        "papers (Mateo et al. 2021; Hermant et al. 2025).",
        "key_quote": "Most faults in the GeoDAWN region of Nevada are more subtle, and many are hidden "
        "below the surface, requiring geophysical data to detect.",
        "status": "fetched and read in full, 2026-09-26",
    },
    {
        "id": "rules-mirror",
        "name": "Official rules page (DrivenData mirror)",
        "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/rules/",
        "what": "A one-line pointer page: the binding rules live in the official rules document hosted by "
        "the prize administrator (HeroX resource 2274, whose PDF is the NLR document below).",
        "key_quote": "Participation in this challenge is subject to the official GEMS Prize rules. "
        "Please review here. (link target: https://www.herox.com/GEMSPrize/resource/2274)",
        "status": "fetched and read in full, 2026-09-26",
    },
    {
        "id": "rules-pdf",
        "name": "Official rules PDF (NLR primary)",
        "url": "https://www.nlr.gov/docs/fy26osti/96647.pdf",
        "what": "'Geologic Enhanced Mapping System (GEMS) Prize Official Rules', September 2026. The "
        "www.nlr.gov address resolves to the same document at docs.nlr.gov/docs/fy26osti/96647.pdf. "
        "Sections read and quotable: 1.3 eligibility; 1.4 prize goals; 2 background (footnote 3 = "
        "GeoDAWN citation; footnote 4 = INGENIOUS citation); 3.2 process overview including the "
        "generative-AI disclosure duty; 3.3 training data; 3.4 feedback limits; 3.5 what to submit; "
        "3.6.1-3.6.5 winner determination; Appendix A terms.",
        "key_quote": "Using generative AI technology in the development of your prize submission is "
        "allowed. However, you must indicate in the narrative (not included in the word count) the extent "
        "to which, if any, you used generative AI technology and how you used it to develop your "
        "submission.",
        "status": "fetched and read (4 of 7 chunks cover sections 1-3.6.5 and A.1 start), 2026-09-26",
    },
    {
        "id": "ref-sol",
        "name": "Reference solution (drivendataorg/gems-prize-reference-solution)",
        "url": "https://github.com/drivendataorg/gems-prize-reference-solution",
        "what": "The organisers' baseline: one commit (aebe92f, 2026-06-16), author Professor John Lipor "
        "(Portland State), a single notebook 'unet-mc-cv-reference-solution.ipynb'. Design read directly "
        "from the cloned notebook (see Prior art).",
        "key_quote": "This repository contains a reference solution for the GEMS Prize Challenge. The "
        "benchmark is implemented in Python and uses standard libraries to provide a baseline for "
        "comparison with other solutions.",
        "status": "repository page fetched; notebook cloned from github.com and read cell by cell, "
        "2026-09-26 (local copy verified by git clone of the published HEAD)",
    },
    {
        "id": "forum",
        "name": "Competition forum (official clarifications)",
        "url": "https://community.drivendata.org/c/gems-prize-challenge/111",
        "what": "Live category. Staff account chrisk-dd posts the official clarifications. Threads read "
        "in raw form this session: 11516 (scoring mask), 11527 (test-fault provenance), 11529 (label "
        "band count). Others catalogued by title: 11524 weekly submissions, 11526 institutional limit, "
        "11528 paid external-data licence, 11536 'where do you draw the line', 11540 team-member "
        "eligibility, 11543 teammate's geological interpretation as training labels.",
        "key_quote": "(chrisk-dd, thread 11516 post 2) Pixels corresponding to known USGS/INGENIOUS "
        "faults are masked / excluded from evaluation, so they do not count towards penalty terms.",
        "status": "category page and raw thread dumps fetched, 2026-09-26",
    },
    {
        "id": "geodawn",
        "name": "GeoDAWN feature-data citation (DOI 10.5066/P93LGLVQ)",
        "url": "https://doi.org/10.5066/P93LGLVQ",
        "what": "Resolves to USGS ScienceBase item 657e1d85d34e23d3533209f7: Glen, J.M.G., and Earney, "
        "T.E., 2024, GeoDAWN: Airborne magnetic and radiometric surveys of the northwestern Great Basin, "
        "Nevada and California. Publication date 2024-03-01; surveys flown 2021-11-01 to 2022-11-20 by "
        "EDCON-PRJ; 149,030 line-km over 51,857 sq km; four acquisition blocks (Winnemucca, Fallon, "
        "Hawthorne, Tonopah); Area 1 (Clayton Valley, lithium focus) rank-1 specs at 200 m line spacing, "
        "Area 2 (geothermal focus) 400 m; magnetic processing includes diurnal, aircraft-field, tie-line "
        "and micro-leveling corrections and IGRF removal.",
        "key_quote": "The combined GeoDAWN area (consisting of a total of 149,030 line-km spanning an "
        "area of 51,857 sq km), was divided into four separate acquisition blocks (from north to south: "
        "Winnemucca, Fallon, Hawthorne, and Tonopah).",
        "status": "DOI resolved; ScienceBase item fetched and read, 2026-09-26",
    },
    {
        "id": "ingenious",
        "name": "INGENIOUS label-data citation (DOI 10.15121/1881483)",
        "url": "https://doi.org/10.15121/1881483",
        "what": "Resolves to DOE Geothermal Data Repository submission 1391 (OpenEI), licence CC-BY 4.0, "
        "'as is' disclaimer. Contains the Quaternary Faults v1 and v2 shapefiles (v2, "
        "qfaults_ingenious_nad83conus117_2023-06-27.zip, supersedes v1; attributes follow the USGS "
        "Qfault schema), earthquake density models, geodetic shear and dilation models, MT conductance "
        "maps, gravity and magnetics maps, heat flow, slip/dilation tendency, and other regional layers.",
        "key_quote": "Shapefile (NAD83 Geographic) containing updated quaternary fault traces, ages, and "
        "slip rates for the INGENIOUS study area. Attributes conform to USGS Qfault Database schema.",
        "status": "DOI resolved; GDR submission page fetched and read, 2026-09-26",
    },
    {
        "id": "qfaults",
        "name": "USGS Quaternary Fault and Fold Database (existing-catalogue baseline)",
        "url": "https://www.usgs.gov/natural-hazards/earthquake-hazards/faults",
        "what": "The current official USGS page for the QFF database (found by search and fetch, not "
        "assumed). Whole-database citation: U.S. Geological Survey, 2020, Quaternary Fault and Fold "
        "Database for the Nation, DOI 10.5066/P9BCVRCK; interactive map DOI 10.5066/F7S75FJM; KMZ and "
        "GIS downloads at earthquake.usgs.gov/static/lfs/nshm/qfaults/. The Database Search function "
        "was retired 2026-02-26; legacy reports remain via the interactive fault map. Database "
        "methodology as stated there: established 1993 under NEHRP with state geological surveys, "
        "compiled from thousands of journal articles, maps, theses and other documents; since "
        "2017-01-12 only a limited set of metadata fields is maintained.",
        "key_quote": "These data are compiled from thousands of journal articles, maps, theses, and "
        "other documents, as referenced herein.",
        "status": "page found by search (URL not hardcoded from memory), fetched and read, 2026-09-26",
    },
    {
        "id": "competition-rasters",
        "name": "Competition rasters (placed and hash-verified 2026-09-26)",
        "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/data/",
        "what": "The three official rasters are now in this repository's data/ directory, every byte "
        "sha256-verified against pins that three independent project records state identically (GEMSDOE "
        "data/bridge/manifest.json, generated 2026-09-17 from a runner-side inventory taken "
        "2026-09-14 from the logged-in data tab; the 8GEMSDOE download script; and the session-6 "
        "evidence file grav_hg_identity_session6.json, whose training_features_sha256 matches the "
        "file placed today). Read back today by scripts/prepare_data.py: training_features.tif = 19 "
        "bands, float32, 3292x3730, 100 m, EPSG:32611; existing_faults.tif = 1 band, int8, same grid; "
        "example_submission.tif = 1 band float32, same grid.",
        "key_quote": "training_features.tif sha256 4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5 "
        "(matches the pin used by gemsdoe_review session 6 against the same bytes).",
        "status": "placed in this sandbox via the project git bridge on 2026-09-26; the DrivenData data "
        "tab itself requires login and was not logged into (by design of this agent)",
    },
]

# ---------------------------------------------------------------------------
# Research domains. `kind` on an entry: official | internal | published | forum.
# ---------------------------------------------------------------------------
DOMAINS = [
    {
        "slug": "potential-field",
        "title": "Potential-field geophysics",
        "flag": "",
        "summary": "Magnetic (RTP, TMI, gradients) and isostatic gravity layers, and what "
        "gradient-magnitude and tilt-derivative operators imply about buried structural contrasts in "
        "this specific survey.",
        "entries": [
            {
                "id": "pf-1",
                "title": "What the GeoDAWN survey physically measured",
                "kind": "official",
                "sources": [("GeoDAWN, USGS ScienceBase (DOI 10.5066/P93LGLVQ)", "https://doi.org/10.5066/P93LGLVQ")],
                "claims": [
                    "Airborne magnetics and radiometrics over 51,857 sq km, 149,030 line-km, four "
                    "acquisition blocks (Winnemucca, Fallon, Hawthorne, Tonopah), flown 2021-11-01 "
                    "through 2022-11-20.",
                    "Area 1 (Clayton Valley, lithium focus) was flown to rank-1 specifications with 200 m "
                    "line spacing; Area 2 (the geothermal-focused remainder) at 400 m line spacing; "
                    "terrain-following flight at nominal 100-150 m (Area 1) / 150-200 m (Area 2) clearance.",
                    "Magnetic processing included diurnal and aircraft-field corrections, tie-line "
                    "leveling, micro-leveling and IGRF removal; radiometric processing corrected for "
                    "radon, Compton scattering and altitude.",
                ],
                "relevance": "The line spacing sets the physical noise floor for any 100 m gradient or "
                "tilt product: in Area 2 the 400 m line spacing is coarser than the competition grid, so "
                "supplied gradients there are interpolated across flight-line gaps. Edge-detector "
                "hypotheses must expect anisotropic along-line vs cross-line noise, strongest in the "
                "south (Tonopah block).",
                "confidence": "High - read from the primary data-release page.",
            },
            {
                "id": "pf-2",
                "title": "Which derivative channels the competition actually supplies",
                "kind": "official",
                "sources": [
                    ("Problem description, Provided features", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features"),
                    ("Our header read of the placed raster (scripts/prepare_data.py, 2026-09-26)", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/scripts/prepare_data.py"),
                ],
                "claims": [
                    "training_features.tif is a 19-band, float32, 100 m, EPSG:32611 GeoTIFF (3292x3730). "
                    "The problem description lists the families: surface conductivity and depth to "
                    "conductive base; detrended elevation and its slope; dilatation rate, shear strain "
                    "rate and second invariant of the strain-rate tensor; isostatic gravity anomaly and "
                    "its slope; reduced-to-pole magnetics, total magnetic intensity, vertical and "
                    "horizontal slope of TMI, and top-of-crustal magnetic source depth; earthquake density.",
                    "The supplied raster has 19 bands and float32 samples - confirmed by direct header "
                    "parse of the placed, hash-verified file on 2026-09-26.",
                ],
                "relevance": "Horizontal-gradient magnitude (HGM), analytic signal and tilt derivatives "
                "must be derived client-side from the supplied anomaly bands; only the raw slope-style "
                "bands are given. Any hypothesis about 'the tilt channel' is really about our own "
                "derivation from tmi or iso_grav_anom.",
                "confidence": "High - official list plus our own verified read of the bytes.",
            },
            {
                "id": "pf-3",
                "title": "The supplied gravity 'hg' band is a signed derivative, not a gradient magnitude",
                "kind": "internal",
                "sources": [
                    ("gemsdoe_review/evidence/grav_hg_identity_session6.json (sha-pinned tool + input)", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/evidence/grav_hg_identity_session6.json"),
                ],
                "claims": [
                    "On the sha-verified training_features.tif (4371c82e...), over 400,000 sampled "
                    "pixels: Spearman(iso_grav_anom_hg, dG/dx) = 0.9485; Spearman(iso_grav_anom_hg, "
                    "HGM) = -0.0002; Spearman(iso_grav_anom_slope, HGM) = 0.9604; Spearman(tmi_hg, HGM) "
                    "= 0.9999999. Verdict recorded in the evidence file: iso_grav_anom_hg is the signed "
                    "E-W derivative dG/dx, NOT |grad G|; iso_grav_anom_slope is the gradient magnitude; "
                    "tmi_hg is the gradient magnitude.",
                ],
                "relevance": "Any gravity 'edge' feature must use iso_grav_anom_slope (or derive |grad| "
                "from iso_grav_anom), not iso_grav_anom_hg. The magnetic band tmi_hg is safe. This was "
                "the session-6 correctness fix; measured transfer effect about +/-0.005 DTI on the "
                "mapped-catalogue CV.",
                "confidence": "High for the measurement (label-free, sha-pinned, re-checkable); the "
                "band-naming intent of the organiser remains unexplained.",
            },
            {
                "id": "pf-4",
                "title": "Tilt-derivative depth estimation is blocked by the supplied bands",
                "kind": "internal",
                "sources": [
                    ("gemsdoe_review/gemsdoe_review/SESSION6.md (items 2 and 'still unverified')", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/SESSION6.md"),
                ],
                "claims": [
                    "The 99th percentile of |tilt derivative| computed from the supplied magnetic bands "
                    "is 3.08 degrees, far below the +/-45 degree contour the classic tilt-depth method "
                    "requires; the TDR is computed from already-smoothed, line-leveled grids rather than "
                    "the raw field.",
                ],
                "relevance": "Do not spend effort on tilt-depth. Edge location (where TDR crosses zero) "
                "remains usable; depth estimation from these bands is not.",
                "confidence": "Medium-high - internal measurement, single-session, method assumption "
                "(that p99 3.08 deg implies the 45 deg contour is absent) stated but not independently "
                "replicated.",
            },
            {
                "id": "pf-5",
                "title": "The organisers' own reading list endorses potential-field mapping",
                "kind": "official",
                "sources": [("About page (page/968), Additional information", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/#additional-information")],
                "claims": [
                    "The official About page states that gravity and magnetic surveys 'help infer the "
                    "presence of faults through density or magnetic anomalies', and that many GeoDAWN "
                    "faults 'are hidden below the surface, requiring geophysical data to detect'.",
                ],
                "relevance": "Official confirmation that the buried-fault population is in scope and "
                "that potential-field layers are a primary detection modality - not just a "
                "supplementary channel.",
                "confidence": "High - verbatim from the official page.",
            },
        ],
    },
    {
        "slug": "geomorphology",
        "title": "DEM-based structural geomorphology",
        "flag": "",
        "summary": "Curvature and breaks-in-slope for scarp detection; what a subtle or partially "
        "buried scarp can look like in this terrain, and what the 1 m DEM adds over the 100 m stack.",
        "entries": [
            {
                "id": "gm-1",
                "title": "A 1 m DEM is provided by link, not in the stack",
                "kind": "official",
                "sources": [
                    ("Problem description, Provided features", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features"),
                    ("Rules PDF section 3.3", "https://www.nlr.gov/docs/fy26osti/96647.pdf"),
                ],
                "claims": [
                    "'In addition, you will find a CSV file called 1m_DEM_links.csv that contains links "
                    "where DEM data at 1m resolution can be downloaded.' (problem description)",
                    "Rules 3.3: 'instructions will be provided for downloading USGS DEM elevation data at "
                    "1-m resolution for the GeoDAWN region.'",
                    "The About page records that airborne lidar was collected through the USGS 3D "
                    "Elevation Program coordinated with the GeoDAWN surveys.",
                ],
                "relevance": "The 100 m stack carries only detrended elevation and its slope. Scarp "
                "morphology (free face, crest base break, back-tilt) lives at metre scale; the 1 m DEM "
                "is the only source that can resolve it. Using it requires downloading and processing "
                "tiles - a real but bounded engineering cost.",
                "confidence": "High - official text, three places.",
            },
            {
                "id": "gm-2",
                "title": "Detrended-elevation slope is the strongest supplied topographic channel",
                "kind": "internal",
                "sources": [
                    ("gemsdoe_review SESSION6 item 2 (DEM curvature / slope break)", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/SESSION6.md"),
                ],
                "claims": [
                    "Session 6 records slope_of_slope (the supplied slope of detrended elevation) as the "
                    "strongest single topographic channel with univariate AUC 0.598 against mapped "
                    "catalogue labels, and leaves curvature/break-in-slope derivatives already in the "
                    "88/105-channel feature set.",
                ],
                "relevance": "Supports the hypothesis that topography contributes real signal even at "
                "100 m, and that finer DEM derivatives are the natural extension rather than a new "
                "modality.",
                "confidence": "Medium - internal, single measurement chain, AUC is univariate and "
                "catalogue-relative.",
            },
            {
                "id": "gm-3",
                "title": "Published precedent: scarps mapped from elevation and slope data in this region",
                "kind": "published",
                "sources": [
                    ("Hermant, Kiersnowski & Bellanger 2025, Stanford Geothermal Workshop (officially cited on page/968)", "https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf"),
                ],
                "claims": [
                    "'Many faults induce local topographic variations (fault scarp) that can be mapped "
                    "from elevation, slope or satellite imagery data' - stated for the Basin and Range / "
                    "Walker Lane study area of the cited paper (northern central Nevada).",
                    "The same paper trains CNNs with lidar-derived labels and reports lidar coverage as "
                    "a first-class input to fault mapping in Nevada.",
                ],
                "relevance": "External, organiser-endorsed precedent that scarp expression in elevation "
                "data is a mapped, learnable signature in this exact region.",
                "confidence": "High - verbatim from the cited paper, read this session.",
            },
            {
                "id": "gm-4",
                "title": "What a partially buried scarp looks like here (working description, not a fact)",
                "kind": "internal",
                "sources": [
                    ("Problem description (misalignment and rasterisation caveats)", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric"),
                    ("Forum thread 11516 post 4 (staff, on corrections near known traces)", "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4"),
                ],
                "claims": [
                    "The official metric text itself warns that 'portions of the existing fault data may "
                    "be misaligned from the true location of the surface fault, which is the prediction "
                    "target' and that rasterisation is lossy near pixel boundaries.",
                    "Staff confirm that a new-fault label 'can indeed lie within 300m of a known fault "
                    "trace' and that such pixels 'would constitute corrections or modifications to "
                    "existing fault traces'.",
                ],
                "relevance": "The realistic DEM signature of a catalogue gap is not a fresh 3 m scarp "
                "but: a subdued or segmented break-in-slope, a drainage-line deflection, or an offset "
                "of the mapped trace by tens to hundreds of metres. Hypotheses must score 'weak scarp "
                "plus structural agreement' rather than expecting sharp scarps everywhere.",
                "confidence": "Reasoning built on verified official statements; the geomorphic "
                "expectation itself is interpretation, marked as such.",
            },
        ],
    },
    {
        "slug": "seismotectonics",
        "title": "Seismotectonics and strain",
        "flag": "",
        "summary": "Strain-rate invariants, earthquake density and conductivity anomalies: where the "
        "independent families agree, where they disagree, and what each disagreement means.",
        "entries": [
            {
                "id": "st-1",
                "title": "Provenance of the strain, seismicity and conductivity bands",
                "kind": "official",
                "sources": [("INGENIOUS compilation, GDR submission 1391 (DOI 10.15121/1881483)", "https://doi.org/10.15121/1881483")],
                "claims": [
                    "The INGENIOUS regional compilation ships: 'Earthquake Density Models' ('independent "
                    "and dependent earthquake density for the INGENIOUS study area'), 'Geodetic Shear and "
                    "Dilation Models', and 'Electrical Conductance Maps - MT' estimated from a 3D model "
                    "of the Great Basin at five depth ranges spanning 2 to 200 km (released as its own "
                    "USGS DOI 10.5066/P9TWT2LU).",
                    "These are the provenance layers behind the competition's dilatation, shear strain, "
                    "second invariant, earthquake density and conductivity bands.",
                ],
                "relevance": "The strain and seismicity bands are model-derived regional products, not "
                "local measurements - their resolution and smoothing are inherited from geodetic "
                "solutions and catalogues, so they cannot localize at 100 m. They identify provinces, "
                "not traces.",
                "confidence": "High - official data-release descriptions.",
            },
            {
                "id": "st-2",
                "title": "Measured agreement and disagreement between the families",
                "kind": "internal",
                "sources": [
                    ("gemsdoe_review SESSION6 item 2 (cross-reference bullet)", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/SESSION6.md"),
                ],
                "claims": [
                    "Session 6 records Spearman(strain, seismicity) = 0.77 - noted as 'largely one belt "
                    "signal' - and univariate AUCs against mapped catalogue labels: independent "
                    "earthquake density 0.583, dependent 0.560, conductivity 0.520.",
                ],
                "relevance": "Strain and seismicity are largely one signal (the Central Nevada seismic "
                "belt). Conductivity is nearly orthogonal to everything else - weak alone, but it is "
                "the only supplied band sensing fluids/brines at depth, which is exactly the burial "
                "masking the catalogue-gap domain cares about.",
                "confidence": "Medium - internal measurements, catalogue-relative AUCs.",
            },
            {
                "id": "st-3",
                "title": "Where families agree vs disagree is itself information",
                "kind": "internal",
                "sources": [
                    ("Problem description (two-round structure; final round rescoring)", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#competition-structure"),
                ],
                "claims": [
                    "The final prize round is scored against an expanded label set built by expert "
                    "review of every submission: 'faults that you flagged, that experts confirm, become "
                    "part of the map of the region.'",
                ],
                "relevance": "A flag that rests on two independent families (e.g. a gravity edge that "
                "also aligns with a seismicity lineament) is a better expert-review candidate than a "
                "single-family edge, even at equal DTI. Cross-family agreement should be logged per "
                "candidate in the dossier, not folded into one blended score.",
                "confidence": "High for the scoring fact; the dossier design follows from it.",
            },
        ],
    },
    {
        "slug": "catalogue-gaps",
        "title": "Catalogue-gap reasoning",
        "flag": "highest-leverage domain - this is the scored target",
        "summary": "Read the INGENIOUS compilation and the USGS database as methodologies, not just as "
        "rasters: how were existing faults actually mapped, and where does that process structurally "
        "fail to look?",
        "entries": [
            {
                "id": "cg-1",
                "title": "The USGS database is a compilation of prior studies, not a systematic survey",
                "kind": "official",
                "sources": [("USGS Quaternary Fault and Fold Database page", "https://www.usgs.gov/natural-hazards/earthquake-hazards/faults")],
                "claims": [
                    "'These data are compiled from thousands of journal articles, maps, theses, and "
                    "other documents, as referenced herein.' The database was begun in earnest in 1993 "
                    "under NEHRP 'with significant support from many State surveys'; the cooperators "
                    "list is state geological surveys (Nevada Bureau of Mines and Geology among them).",
                    "Since 2017-01-12 USGS maintains 'a limited number of metadata fields'; the "
                    "Database Search function was retired 2026-02-26 with legacy reports accessible "
                    "through the interactive fault map.",
                ],
                "relevance": "Coverage therefore tracks where fieldwork, theses and state mapping "
                "happened - population corridors, parklands, mineral districts - not where faults are. "
                "This is the single most important structural fact about the catalogue: absence of a "
                "trace is evidence about mapping history, not about the fault.",
                "confidence": "High - verbatim from the database's own page.",
            },
            {
                "id": "cg-2",
                "title": "INGENIOUS faults are an update-and-merge of the USGS schema, with version lag",
                "kind": "official",
                "sources": [("INGENIOUS compilation, GDR submission 1391 (DOI 10.15121/1881483)", "https://doi.org/10.15121/1881483")],
                "claims": [
                    "'Quaternary Faults v1.zip - Shapefile (NAD83 Geographic) containing updated "
                    "quaternary fault traces, ages, and slip rates for the INGENIOUS study area. "
                    "Attributes conform to USGS Qfault Database schema.'",
                    "'Quaternary Faults v2.zip - This archive contains an updated version of the "
                    "INGENIOUS quaternary fault compilation shapefile... It supersedes Quaternary Faults "
                    "v1' (file dated 2023-06-27).",
                    "The competition labels come 'from the USGS quaternary fault maps and from "
                    "INGENIOUS' (problem description), and rules 3.3 states training labels were "
                    "'obtained from the INGENIOUS project's Great Basin Regional Dataset Compilation'.",
                ],
                "relevance": "The catalogue we train on is a merge of the USGS compilation with "
                "INGENIOUS updates - compiled twice, from inherited sources, with a visible revision "
                "history. Version lag is demonstrable (v1 superseded by v2 within the project's own "
                "lifetime), so 'the catalogue is a snapshot that lags the landscape' is grounded, not "
                "speculative.",
                "confidence": "High - official data-release text.",
            },
            {
                "id": "cg-3",
                "title": "Published, organiser-cited evidence that mapping density is artificial",
                "kind": "published",
                "sources": [
                    ("Hermant et al. 2025 (cited on page/968)", "https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf"),
                ],
                "claims": [
                    "'their accuracy and the homogeneity of mapping between the sub-regions/states is "
                    "sometimes insufficient... This could create a bias between regions where fault "
                    "mapping is robust and those where it is incomplete.'",
                    "'some areas where the geology has been mapped more precisely have an artificially "
                    "higher fault density and accuracy than areas where geological and structural "
                    "mapping has been done at a larger scale.'",
                    "Their Figure 2 documents 'regional variation in Quaternary fault mapping that is "
                    "not only due to the geological context' and local discrepancies 'up to 400m' "
                    "between USGS Quaternary faults and their own ground-truth labels in north-central "
                    "Nevada.",
                ],
                "relevance": "The strongest external support for the catalogue-gap thesis, and it is "
                "organiser-cited. It also gives a concrete magnitude for positional error (hundreds of "
                "metres) consistent with the official 300 m metric kernel.",
                "confidence": "High - verbatim from the PDF, read this session.",
            },
            {
                "id": "cg-4",
                "title": "The test-fault identification process is officially undisclosed",
                "kind": "forum",
                "sources": [
                    ("Forum thread 11527, staff reply (chrisk-dd, 2026-09-23)", "https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7"),
                ],
                "claims": [
                    "Asked directly which data sources, fault types and coverage the experts used, the "
                    "staff reply is: 'We're not sharing details about the data sources, fault types, or "
                    "coverage behind the test faults beyond what's in the problem description.'",
                ],
                "relevance": "No shortcut exists: the catalogue-gap model must be reasoned from the "
                "catalogue's own methodology and the geophysics, not from leaked test-set "
                "characteristics. Any competitor claiming knowledge of test-fault provenance is "
                "claiming something the organisers say they did not disclose.",
                "confidence": "High - verbatim staff statement.",
            },
            {
                "id": "cg-5",
                "title": "The scoring mask is pixel-exact and corrections are in scope",
                "kind": "forum",
                "sources": [
                    ("Forum thread 11516, staff posts 2 and 4", "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4"),
                ],
                "claims": [
                    "'Pixels corresponding to known USGS/INGENIOUS faults are masked / excluded from "
                    "evaluation' in both rounds; 'The mask is indeed pixel-exact - it is identical to "
                    "the provided set of training fault labels.'",
                    "'Only new-fault ground truth is considered for scoring purposes. A predicted pixel "
                    "that is near a known fault trace but far from a new-fault ground truth pixel will "
                    "be fully penalized.'",
                    "'A new-fault ground truth pixel can indeed lie within 300m of a known fault trace. "
                    "Such pixels would constitute corrections or modifications to existing fault "
                    "traces.'",
                ],
                "relevance": "Three direct design consequences: (1) reproducing known traces earns "
                "nothing; (2) splay/tip predictions hugging known traces carry real false-positive cost "
                "because no buffer shields them; (3) corrections of misaligned known traces are an "
                "explicitly stated target - and the published 400 m discrepancies (Hermant Fig. 2) show "
                "such corrections exist at scale.",
                "confidence": "High - verbatim staff statements.",
            },
            {
                "id": "cg-6",
                "title": "Where the catalogue should structurally be incomplete (reasoned hypothesis set)",
                "kind": "internal",
                "sources": [
                    ("Compilation methodology facts in cg-1/cg-2; masking facts in cg-5; survey facts in pf-1", "https://github.com/buffedlizard55-lab/SelfLearn/tree/main/docs/research"),
                ],
                "claims": [
                    "From how the catalogue was made (compilation of historical studies + partial "
                    "update), four structural gap classes follow, each testable against the supplied "
                    "layers: (a) basin-interior areas where young, fine-grained cover masks scarps and "
                    "old fieldwork was sparse - detectable as low-relief + conductive cover + gravity "
                    "lineaments; (b) high-relief remote ranges where access limited fieldwork - "
                    "ruggedness + sparse catalogue density + magnetic/gravity edges; (c) along-strike "
                    "continuations and splays beyond mapped tips - the mapping stopped, the structure "
                    "did not; (d) misaligned traces needing correction - catalogue line offset from the "
                    "actual scarp/edge by tens to hundreds of metres.",
                ],
                "relevance": "This is the working taxonomy for gap-hunting: each class pairs a "
                "catalogue-methodology reason with a detectable multi-layer signature, which is "
                "exactly what the final-round expert review rewards.",
                "confidence": "Reasoned from verified facts; each class is a hypothesis, not a finding.",
            },
        ],
    },
    {
        "slug": "prior-art",
        "title": "Prior art",
        "flag": "",
        "summary": "Published fault/lineament-extraction ML applicable to this feature stack, and the "
        "reference solution's specific design choices read from its own code.",
        "entries": [
            {
                "id": "pa-1",
                "title": "Mateo et al. 2021 - U-Net fault mapping in optical images and topography",
                "kind": "published",
                "sources": [
                    ("Mateo, L., Manighetti, I., Tarabalka, Y., et al. (2021), JGR Solid Earth 126, e2020JB021269, DOI 10.1029/2020JB021269", "https://doi.org/10.1029/2020JB021269"),
                ],
                "claims": [
                    "Open-access JGR Solid Earth paper (first published 2021-04-01): 'we have adopted a "
                    "machine learning approach, namely a U-Net Convolutional Neural Network (CNN), to "
                    "automate the identification and mapping of fractures and faults in optical images "
                    "and topographic data', trained on 'a moderate amount of manually created fracture "
                    "and fault maps of low resolution and basic quality'; the selected model MRef "
                    "'exhibits good generalization capacities'.",
                    "Officially listed in the competition About page's additional information.",
                ],
                "relevance": "Establishes that U-Net segmentation trained on imperfect, incomplete "
                "manual maps generalises across image types - directly relevant to training on the "
                "incomplete catalogue. Also a caution: its inputs are images/topography, not "
                "potential-field grids, so transfer to 19-band geophysics is unproven.",
                "confidence": "High - abstract read from the publisher page this session.",
            },
            {
                "id": "pa-2",
                "title": "Hermant et al. 2025 - CNN Quaternary fault mapping in the western USA",
                "kind": "published",
                "sources": [
                    ("Hermant, B., Kiersnowski, L., & Bellanger, M. (2025), 50th Stanford Geothermal Workshop (officially cited on page/968)", "https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf"),
                ],
                "claims": [
                    "TLS Geothermics' CNN approach 'using remote sensing images' produces regional fault "
                    "prediction maps, motivated explicitly by USGS catalogue bias (see cg-3), with "
                    "lidar coverage as an input and a study area in northern central Nevada.",
                ],
                "relevance": "The closest published analogue to this competition's task and region, by "
                "an industry group, officially cited by the organisers. Their stated motivation - "
                "correcting catalogue bias - is the catalogue-gap domain in one sentence.",
                "confidence": "High - PDF read this session.",
            },
            {
                "id": "pa-3",
                "title": "The reference solution, read from its own notebook (commit aebe92f)",
                "kind": "official",
                "sources": [
                    ("drivendataorg/gems-prize-reference-solution", "https://github.com/drivendataorg/gems-prize-reference-solution"),
                ],
                "claims": [
                    "Single notebook, segmentation_models_pytorch U-Net on PyTorch; patches of 128 px; "
                    "5 Monte Carlo train/test splits; test_proportion 0.5; batch 32; 5 epochs; lr 1e-4; "
                    "TverskyLoss with alpha=0.2, beta=0.8 (matching the metric); per-channel min-max "
                    "normalisation to [0,1] with values < -1e38 set to NaN; random test patches zeroed "
                    "in the global image 'so that there is no leakage between training and test "
                    "datasets'; augmentations RandomResizedCrop/flips/30 deg rotation.",
                    "Output: the averaged probability map cropped to the label grid and written as one "
                    "float32 GeoTIFF band with the label file's CRS and transform; the notebook notes "
                    "'it may be advantageous to threshold this map for better scoring' and plots a "
                    "0.1 threshold example.",
                    "Staff (thread 11529) confirm a known notebook defect: the printed band summary "
                    "labels the single-band label raster 'Band 19' - 'in actuality, only one band'.",
                ],
                "relevance": "The baseline's specific weak points, each visible in its own code: "
                "(1) random patch splits on connected fault traces leak spatial context, so its "
                "internal validation overstates spatial generalisation; (2) min-max normalisation is "
                "outlier-driven; (3) 5 epochs with no threshold calibration ships an uncalibrated "
                "surface; (4) it never touches the 1 m DEM; (5) it treats the catalogue as complete "
                "truth, which the problem description explicitly says it is not.",
                "confidence": "High - read from the notebook source this session; interpretations of "
                "the weaknesses are ours and labelled as such.",
            },
        ],
    },
    {
        "slug": "governance",
        "title": "Competition governance",
        "flag": "time-sensitive items tracked here",
        "summary": "Rules, deadlines, disclosure duties, eligibility triggers, and every official "
        "erratum or clarification worth tracking.",
        "entries": [
            {
                "id": "go-1",
                "title": "Key dates and structure",
                "kind": "official",
                "sources": [("Competition hub", "https://www.drivendata.org/competitions/306/competition-doe-gems/")],
                "claims": [
                    "Competition end date: Dec. 3, 2026, 11:59 p.m. UTC. Total prize pool $300,000: "
                    "Initial Prize Round $50,000 (top 5, $10,000 each, private test set); Final Prize "
                    "Round $250,000 (top 5 on the re-labeled dataset: $100k/$70k/$40k/$25k/$15k).",
                    "A single chosen submission is scored in both rounds; the choice must be made "
                    "before the deadline 'without knowledge of your scores on the private test set' "
                    "(rules 3.6.2).",
                ],
                "relevance": "Time budget: about 10 weeks remain after 2026-09-26. Everything this "
                "agent produces should compound toward one blind submission choice.",
                "confidence": "High - official pages.",
            },
            {
                "id": "go-2",
                "title": "Submission and feedback limits",
                "kind": "official",
                "sources": [("Rules PDF 3.2 and 3.4", "https://www.nlr.gov/docs/fy26osti/96647.pdf")],
                "claims": [
                    "'You can make multiple submissions, subject to the limits specified on the "
                    "competition website (three submissions per week).' (3.2)",
                    "'each participating entity may submit... up to three per week... By the submission "
                    "deadline, you must select only one set of predictions... Multiple finalized "
                    "submissions are not allowed... individuals participating on a team will not be "
                    "allowed to submit a separate final submission.' (3.4)",
                ],
                "relevance": "This agent never generates or uploads submissions (hard project "
                "constraint); the limits are tracked so downstream, gated processes stay compliant.",
                "confidence": "High - official rules text.",
            },
            {
                "id": "go-3",
                "title": "Generative-AI disclosure duty (rules 3.2) and this project's compliance",
                "kind": "official",
                "sources": [
                    ("Rules PDF 3.2", "https://www.nlr.gov/docs/fy26osti/96647.pdf"),
                    ("This site's AI-usage log", "../ai-usage-log.html"),
                ],
                "claims": [
                    "Verbatim duty: 'you must indicate in the narrative (not included in the word "
                    "count) the extent to which, if any, you used generative AI technology and how you "
                    "used it to develop your submission'; competitors own 'the accuracy, authenticity, "
                    "and authorship representations of your submission', with 'research misconduct "
                    "resulting from fabrication, falsification, or plagiarism' named as the risk.",
                ],
                "relevance": "The reason the AI-usage log is a first-class site artifact built "
                "incrementally: the disclosure must be accurate at deadline, so it is written as the "
                "work happens, not reconstructed.",
                "confidence": "High - verbatim rules text.",
            },
            {
                "id": "go-4",
                "title": "Eligibility (rules 1.3) and the re-confirmation trigger",
                "kind": "official",
                "sources": [("Rules PDF 1.3", "https://www.nlr.gov/docs/fy26osti/96647.pdf")],
                "claims": [
                    "Individual competitors must be U.S. citizens or permanent residents; teams need a "
                    "U.S.-citizen/permanent-resident captain and members 'legally authorized to work in "
                    "the United States'; private entities must be U.S.-incorporated with primary place "
                    "of business in the U.S.; FFRDC-affiliated researchers may compete individually "
                    "only without FFRDC resources (honourable mention only); non-DOE federal employees "
                    "and entities are ineligible; MFTRP participants and FCOC-controlled entities are "
                    "ineligible; registration includes a signed certification 'under penalty of "
                    "perjury'.",
                ],
                "relevance": "Standing trigger in this project's charter: if team composition or "
                "affiliations change, re-check 1.3 before anything else. Eligibility is 'subject to "
                "verification before prizes are awarded'.",
                "confidence": "High - official rules text.",
            },
            {
                "id": "go-5",
                "title": "Errata and clarifications ledger (running)",
                "kind": "forum",
                "sources": [("GEMS Prize Challenge forum category", "https://community.drivendata.org/c/gems-prize-challenge/111")],
                "claims": [
                    "2026-09-16/21: scoring mask is pixel-exact, known faults excluded in both rounds, "
                    "corrections within 300 m are in scope (thread 11516).",
                    "2026-09-23: test-fault data sources/fault types/coverage not disclosed (thread "
                    "11527); reference-notebook 'Band 19' label is an acknowledged summary-string bug, "
                    "the label raster has one band (thread 11529).",
                    "Open threads this session did not need to resolve: weekly-submission mechanics "
                    "(11524), institutional limit (11526), paid external-data licence (11528), 'where "
                    "do you draw the line' (11536), team-member eligibility homepage-vs-rules (11540), "
                    "teammate interpretation as training labels (11543). Listed for the next pass.",
                ],
                "relevance": "The ledger is the governance domain's output: anything time-sensitive or "
                "rule-changing lands here with its date.",
                "confidence": "High for the three read threads; the rest are catalogued by title only.",
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# Hypothesis backlog. Statuses: untested | validated-on-spatial-holdout | rejected.
# 'dti_impact' is expected impact on the distance-weighted Tversky index; internal
# numbers are mapped-catalogue transfer proxies, never leaderboard scores.
# ---------------------------------------------------------------------------
HYPOTHESES = [
    {
        "id": "H-G1",
        "title": "Gravity edge = gradient magnitude, not the supplied hg band",
        "layers": "iso_grav_anom, iso_grav_anom_slope (channels 25/26 rebuilt)",
        "signature": "|grad G| edges along density contrasts; range-front and basin-edge lineaments",
        "gap_reasoning": "Buried range-front faults produce gravity gradients where the surface shows "
        "no scarp; using the correct magnitude keeps those edges while the signed dG/dx band doubles "
        "counted edges and misplaces sign information.",
        "dti_impact": "+0.005 mapped-catalogue CV at 88 channels (session 6, 0.2397 vs 0.2345); "
        "neutral at 105 channels",
        "cost": "Trivial - channel rebuild, no new data",
        "status": "validated-on-spatial-holdout",
        "status_detail": "Passes non-inferiority on the pre-registered rule at 88 channels; at 105 "
        "channels it fails the fold clause by 0.0003. Adopted as a correctness fix, not a score lever.",
        "sources": [
            ("grav_hg_identity_session6.json", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/evidence/grav_hg_identity_session6.json"),
            ("SESSION6 item 2", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/SESSION6.md"),
        ],
    },
    {
        "id": "H-G2",
        "title": "105-channel feature set (adds dead-band replacements and curvature stack)",
        "layers": "full 19 official bands + derived HGM/ASA/tilt, multi-scale curvature, breaks-in-slope, structure-tensor lineaments",
        "signature": "richer edge/lineament geometry across scales",
        "gap_reasoning": "More complete edge chemistry raises recall on subtle structural contrasts "
        "that the 19 raw bands under-specify.",
        "dti_impact": "+0.0074 mapped-catalogue CV (0.2419 vs 0.2345, 3/4 folds better, single seed)",
        "cost": "Low - engineering only",
        "status": "validated-on-spatial-holdout",
        "status_detail": "Adopted by pre-registered rule in session 6. Single seed - replication with "
        "seeds 11 and 13 is the standing caveat before treating 105>88 as settled.",
        "sources": [
            ("feature_arm_105_session6.json", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/evidence/feature_arm_105_session6.json"),
        ],
    },
    {
        "id": "H-G3",
        "title": "Tilt-derivative depth estimation from supplied bands",
        "layers": "tmi, iso_grav_anom derivatives",
        "signature": "TDR +/-45 deg contours as depth estimators",
        "gap_reasoning": "Would convert edges to depths, constraining which lineaments are shallow "
        "enough to be catalogue-scale faults.",
        "dti_impact": "None expected - infeasible",
        "cost": "Avoided",
        "status": "rejected",
        "status_detail": "Supplied bands are line-levelled and smoothed: p99 |TDR| is 3.08 deg, so the "
        "45 deg contour does not exist in these grids. Edge location stays usable; depth does not.",
        "sources": [("SESSION6 item 2", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/SESSION6.md")],
    },
    {
        "id": "H-CG1",
        "title": "Buried-basin faults: conductive cover + gravity edge + low relief",
        "layers": "surface conductivity, depth to conductive base, iso_grav_anom |grad|, detrended elevation slope",
        "signature": "low-relief basin interior where a gravity/magnetic lineament crosses high "
        "conductivity with shallow depth-to-base",
        "gap_reasoning": "Class (a) of cg-6: young fine-grained cover masks scarps and historical "
        "fieldwork concentrated elsewhere; the catalogue's own compilation methodology predicts gaps "
        "exactly where cover hides expression and access was easy to avoid. Expert reviewers "
        "distinguishing 'geophysics-only' structures is officially in scope (page/968 explicitly says "
        "many faults are hidden below the surface).",
        "dti_impact": "Unknown until screened; candidate votes exist (gravity-edge + strain areas in "
        "session 6 dossiers)",
        "cost": "Low - supplied channels only",
        "status": "untested",
        "status_detail": "Needs the label-blind screen applied to a basin-mask variant, then a geology "
        "dossier per flag.",
        "sources": [
            ("Catalogue-gap domain, entry cg-6", "domains/catalogue-gaps.html"),
            ("GeoDAWN survey specs (pf-1)", "https://doi.org/10.5066/P93LGLVQ"),
        ],
    },
    {
        "id": "H-CG2",
        "title": "Along-strike tip extensions and splays of mapped systems",
        "layers": "all edge families + catalogue distance surface",
        "signature": "edge continuity beyond mapped tips; parallel splays 1-10 px off known traces",
        "gap_reasoning": "Class (c): mapping stops at the mapped tip, the structure does not. BUT the "
        "staff-stated pixel-exact mask means near-trace false positives are fully penalised (no "
        "buffer applies to known faults), so this hypothesis only pays where continuity evidence is "
        "strong; corrections of misaligned traces (within 300 m) are explicitly in scope.",
        "dti_impact": "Two-sided: gains corrections, costs false splays. Needs an evidence gate "
        "(e.g. require >=2 families) before emitting near known traces",
        "cost": "Low",
        "status": "untested",
        "status_detail": "Design constraint derived from thread 11516/4; the session-6 label-blind "
        "screen already warns that most near-label flags are label-dependent (118 of 943 survive).",
        "sources": [
            ("Forum 11516 post 4", "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4"),
            ("label_blind_corroboration_session6.json", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/evidence/label_blind_corroboration_session6.json"),
        ],
    },
    {
        "id": "H-CG3",
        "title": "Coverage-bias prior from external catalogue attributes",
        "layers": "external: USGS QFaults GIS attributes (age, slip rate, study-reference metadata), INGENIOUS v1 vs v2 diff",
        "signature": "regions where the catalogue's own attributes are thin (old references, sparse "
        "slip-rate fields) and v1->v2 changed traces",
        "gap_reasoning": "Class (a/b) detector built from the catalogue's methodology: attribute "
        "poverty marks places the compilation is stale. External data is explicitly encouraged "
        "(hub page) provided licences permit; both datasets are US public domain / CC-BY.",
        "dti_impact": "Unknown; priors feed sampling weights, not direct scores",
        "cost": "Medium - external data engineering + licence check",
        "status": "untested",
        "status_detail": "Blocked on nothing technical; needs a decision that the modelling line "
        "consumes priors (research-side only for now).",
        "sources": [
            ("USGS QFF page + downloads", "https://www.usgs.gov/natural-hazards/earthquake-hazards/faults"),
            ("INGENIOUS GDR 1391 (CC-BY 4.0)", "https://doi.org/10.15121/1881483"),
        ],
    },
    {
        "id": "H-D1",
        "title": "1 m DEM scarp stack (curvature, break-in-slope, hillshade continuity)",
        "layers": "1m_DEM_links.csv tiles aggregated to 100 m; ridge/valley continuity along strike",
        "signature": "subdued scarps, deflected drainages, segmented free faces",
        "gap_reasoning": "The only layer that resolves scarp morphology; published regional precedent "
        "(Hermant 2025) maps faults from elevation/slope with CNNs, and the organisers provide the "
        "links for exactly this purpose.",
        "dti_impact": "Unknown; likely helps the correction class (misplaced traces) most",
        "cost": "High - tile download, storage, processing",
        "status": "untested",
        "status_detail": "Deferred until the GPU modelling line is resourced; features alone justify "
        "the download.",
        "sources": [
            ("Problem description, 1m_DEM_links.csv", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features"),
            ("Hermant et al. 2025", "https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf"),
        ],
    },
    {
        "id": "H-S1",
        "title": "Cross-family consensus vote (edge + strain + seismicity alignment)",
        "layers": "gravity/magnetic edges, strain invariants, earthquake density",
        "signature": "multi-family lineament agreement",
        "gap_reasoning": "Independent families agreeing on a structure is the strongest "
        "expert-review-friendly evidence; strain and seismicity are province-scale (Spearman 0.77 "
        "between them), so the vote should use them as province priors, not trace evidence.",
        "dti_impact": "DTI-neutral by design; targets final-round expert expansion instead",
        "cost": "Low",
        "status": "validated-on-spatial-holdout",
        "status_detail": "Partially - the session-6 label-blind screen shows only 118/943 flagged "
        "components survive without local labels; multi-family flags were mostly label-dependent. "
        "Conclusion: consensus must be computed label-blind and reported per candidate in the "
        "dossier, not blended into the score.",
        "sources": [
            ("label_blind_corroboration_session6.json", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/evidence/label_blind_corroboration_session6.json"),
            ("SESSION6 geology section", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/SESSION6.md"),
        ],
    },
    {
        "id": "H-P1",
        "title": "Sparse placement (top-3% of footprint, spacing 4) over dense probability surface",
        "layers": "model probability surface + placement policy",
        "signature": "emission policy, not a new signal",
        "gap_reasoning": "Under the pixel-exact mask and DTI's false-positive term, emitting "
        "confident sparse pixels beats a dense surface: the shipped dense file scored 0.0925 vs "
        "0.2345 for raw/3%/spacing-4 on mapped-catalogue spatial CV, and dense fell below the "
        "matched random control.",
        "dti_impact": "+0.142 mapped-catalogue CV (largest single measured lever)",
        "cost": "None beyond policy code",
        "status": "validated-on-spatial-holdout",
        "status_detail": "Sessions 5 and 6; nested check kept the frozen policy. Numbers are "
        "catalogue-transfer proxies, not leaderboard scores - the mask explanation (11516) is why "
        "the dense policy was doomed.",
        "sources": [
            ("spatial_comparison_shipping_session5.json", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/evidence/spatial_comparison_shipping_session5.json"),
            ("Forum 11516", "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4"),
        ],
    },
    {
        "id": "H-X1",
        "title": "Reference-solution random patch splits overstate generalisation",
        "layers": "validation design",
        "signature": "n/a - evaluation methodology",
        "gap_reasoning": "Connected fault traces span patches; random patch test sets share trace "
        "context with training patches. The notebook's own no-leakage claim holds for pixels, not "
        "for spatial autocorrelation.",
        "dti_impact": "Protects against a systematically optimistic local score",
        "cost": "Already paid",
        "status": "validated-on-spatial-holdout",
        "status_detail": "The project's blocked, buffered, system-purged CV (0-overlap geometry "
        "recorded per fold) exists because of this; dense-vs-spaced measurements above all use it.",
        "sources": [
            ("Reference notebook, patch-split section (markdown cell 9 + make_patches)", "https://github.com/drivendataorg/gems-prize-reference-solution/blob/main/unet-mc-cv-reference-solution.ipynb"),
            ("cv_geometry_audit_2026-09-26.json", "https://github.com/buffedlizard55-lab/SelfLearn/blob/main/gemsdoe_review/evidence/cv_geometry_audit_2026-09-26.json"),
        ],
    },
]

# ---------------------------------------------------------------------------
# AI-usage compliance log (rules 3.2). Append-only, dated, first-class.
# ---------------------------------------------------------------------------
AI_LOG = [
    {
        "date": "2026-09-26",
        "session": "Research-library session 7 (this site)",
        "actor": "Arena.ai Agent Mode autonomous agent (language-model-based), working unattended in "
        "the SelfLearn repository",
        "tools": [
            "Arena page-fetch infrastructure: read the official competition hub, problem description, "
            "About page, rules mirror, rules PDF (4 chunks), forum category + raw threads 11516/11527/11529, "
            "reference-solution repo page, ScienceBase GeoDAWN item, GDR 1391 item, USGS QFF page, "
            "Mateo 2021 landing page, Hermant 2025 PDF, 6GEMSDOE site",
            "git clone (read-only) of github.com/drivendataorg/gems-prize-reference-solution at HEAD "
            "aebe92f and of buffedlizard55-lab/GEMSDOE data/bridge via the placement script",
            "GitHub REST API via gh (read-only): repo/Pages/contents listings for the buffedlizard55-lab org",
            "Local file writes: scripts/, docs/research/, evidence/gems/, tool + JSON exports",
        ],
        "actions": [
            "Verified every source anchor line by line against the live official pages; recorded the "
            "register on this site with quotes",
            "Placed and sha256-verified the three official competition rasters into data/ "
            "(no DrivenData login, no credentials, no account creation)",
            "Wrote scripts/download_competition_data.sh and scripts/prepare_data.py (pure stdlib)",
            "Built this research library: six domain pages, hypothesis backlog, changelog, this log",
            "Created the pull request and merged it to this repository's main branch",
        ],
        "not_done": [
            "No prediction file was generated, validated or submitted; no weekly submission slot was "
            "used; no DrivenData login occurred",
            "No second site, repository or account was created; no competitor's data was used",
        ],
        "compliance_notes": "Rules 3.2 requires the submission narrative to state the extent of "
        "generative-AI use and flags fabrication/falsification/plagiarism as the competitor's own "
        "risk. This log exists so that narrative can be written accurately: every research claim on "
        "this site cites a fetched official source or a committed, re-checkable measurement; quotes "
        "are verbatim; anything not traceable is marked unverified.",
    },
]

# ---------------------------------------------------------------------------
# Changelog (this research section, newest first).
# ---------------------------------------------------------------------------
CHANGELOG = [
    {
        "date": "2026-09-26",
        "items": [
            "Research section created: index, six domain libraries (potential-field, geomorphology, "
            "seismotectonics, catalogue-gaps, prior art, governance), hypothesis backlog (10 entries), "
            "anchor register (11 verified anchors), AI-usage log, this changelog, data-placement page.",
            "PROJECT BLOCKER CLEARED: data placement completed in this repository. "
            "scripts/download_competition_data.sh placed all three official rasters from the project "
            "git bridge with per-part and whole-file sha256 verification (training_features.tif "
            "4371c82e..., existing_faults.tif 7ba308cc..., example_submission.tif 2176d08e...); "
            "scripts/prepare_data.py read them back: 19-band float32 features, 1-band labels, "
            "1-band float32 template, all EPSG:32611 at 100 m, 3292x3730 - conforming to the official "
            "spec. The train->inference->validate pipeline is no longer blocked on data placement "
            "(training itself still needs a GPU machine).",
            "Anchor verification: all eleven source anchors fetched and read on 2026-09-26 "
            "(including the two officially cited prior-art papers and the USGS QFF database page, "
            "whose current URL was found by search rather than assumed).",
            "Irregularities flagged (see index): PROJECT_BRIEF_GEMSDOE.md is absent from the "
            "repository and its git history; 'nlr.gov' resolves via redirect to 'docs.nlr.gov' for "
            "the rules PDF; six GEMS-named repositories currently publish sites while the project "
            "charter says one entity/one site; this sandbox's direct network egress blocks "
            "drivendata.org, usgs.gov, nlr.gov and dropbox.com, so official-page fetches used the "
            "platform's fetch infrastructure and byte transport used the GitHub git bridge.",
        ],
    },
]

# ---------------------------------------------------------------------------
# Irregularities register (flag, never smooth over).
# ---------------------------------------------------------------------------
IRREGULARITIES = [
    {
        "id": "IRR-1",
        "flag": "PROJECT_BRIEF_GEMSDOE.md does not exist",
        "detail": "The session instruction says to read PROJECT_BRIEF_GEMSDOE.md 'in full before doing "
        "anything else'. No file of that name exists anywhere in this repository or its git history. "
        "The session proceeded on the mission text embedded in the instruction itself. If a brief "
        "file exists elsewhere, it should be committed and this section reconciled against it.",
        "status": "open - needs the account holder to supply or confirm the brief",
    },
    {
        "id": "IRR-2",
        "title": "Rules-PDF host spelling",
        "detail": "Session materials variously cite www.nlr.gov and docs.nlr.gov for the rules PDF. "
        "Verified 2026-09-26: www.nlr.gov/docs/fy26osti/96647.pdf resolves (redirect) to "
        "docs.nlr.gov/docs/fy26osti/96647.pdf - one document, two host spellings. This site cites the "
        "www address as given and records the final address.",
        "status": "resolved (documented)",
    },
    {
        "id": "IRR-3",
        "title": "Multiple GEMS-named repositories/sites vs the one-entity charter",
        "detail": "buffedlizard55-lab currently holds twelve GEMS-named repositories, six of which "
        "serve GitHub Pages sites (GEMSDOE, GEMSDOE4, 5GEMSDOE, 6GEMSDOE, 7GEMSDOE, 8GEMSDOE, "
        "LEARNGEMSDOE among them). The charter for this agent says one registered entity and one "
        "site; the 6GEMSDOE site itself declares 'This repository is the one canonical entry' and "
        "flags the duplicates. Session-6 additionally flagged pushes to sibling repos outside its "
        "session window. Nothing here was created, pushed or duplicated; this research section lives "
        "in the existing SelfLearn site only.",
        "status": "open - account-holder cleanup decision (archiving duplicates)",
    },
    {
        "id": "IRR-4",
        "title": "Sandbox egress vs source verification",
        "detail": "This sandbox's direct network can reach github.com and pypi.org only; "
        "drivendata.org, community.drivendata.org, usgs.gov, sciencebase.gov, nlr.gov, osti.gov, "
        "doi.org, openei.org and dropbox.com are blocked at the network layer. Consequences, handled "
        "openly: official-page verification used the platform's fetch infrastructure (recorded per "
        "anchor); the competition rasters were transported through the project's own sha256-pinned "
        "git bridge rather than the blocked mirrors; the mirror URLs remain in the placement script "
        "for machines with unrestricted egress.",
        "status": "mitigated (methods recorded; re-run tools/verify_links.py from a runner for a "
        "fresh machine-readable check)",
    },
    {
        "id": "IRR-5",
        "title": "Brief-score accounts and synchronised submissions (carried from session 6)",
        "detail": "Prior review sessions found the project brief's quoted leaderboard scores appearing "
        "under other accounts' names, and three accounts whose last submissions share one timestamp "
        "near the GEMSDOE3 site's three-file upload. Not verifiable from public pages; flagged, not "
        "interpreted. Carried forward unchanged - this session did no leaderboard scraping.",
        "status": "open (carried) - account-holder awareness only",
    },
]
