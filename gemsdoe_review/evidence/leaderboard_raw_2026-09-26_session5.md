# Public leaderboard — raw transcript (platform page fetcher)

Source: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>
Fetched: 2026-09-26 (session 5, this session) via the platform page fetcher, two
chunks concatenated below. Nothing here is our own score: this workspace has no
DrivenData session and no owned submission. The table is reproduced as fetched so
the parsing in `tools/leaderboard_snapshot.py` can be re-run against these bytes.

| Rank | Participant | Best public DW-Tversky | Submissions | Last submission |
| --- | --- | ---: | ---: | --- |
| 1 | DARD | 0.3049 | 10 | 3d 19h ago |
| 2 | alexoktaba | 0.2993 | 13 | 1d 18h ago |
| 3 | HardcoreTechGod | 0.2854 | 6 | 1w 1d ago |
| 4 | mzoorob | 0.2843 | 15 | 1d 17h ago |
| 5 | joeyfezster | 0.2589 | 12 | 1d ago |
| 6 | GrigorSargsyan | 0.2504 | 5 | 1d 18h ago |
| 7 | xiaofanhu | 0.2367 | 2 | 1d 11h ago |
| 8 | exposed | 0.2340 | 12 | 18h 26min ago |
| 9 | hiii12345 | 0.2262 | 6 | 5h 45min ago |
| 10 | tchu | 0.2220 | 11 | 1d 13h ago |
| 11 | oshbocker | 0.2185 | 15 | 2d 18h ago |
| 12 | moongrega | 0.2174 | 10 | 2d 17h ago |
| 13 | Batik Shirt Brothers (rariwa, masterozone0617) | 0.1956 | 11 | 2d 13h ago |
| 14 | doegemsDrivendata | 0.1847 | 5 | 6d 14h ago |
| 15 | ndavis7 | 0.1797 | 2 | 22h 16min ago |
| 16 | ad3002 | 0.1770 | 11 | 2d 3h ago |
| 17 | nsabaj | 0.1744 | 3 | 16h 34min ago |
| 18 | jgaines | 0.1694 | 12 | 1d 18h ago |
| 19 | dmitry_v | 0.1672 | 3 | 1d 8h ago |
| 20 | hall4jm | 0.1642 | 7 | 1h 35min ago |
| 21 | VictorCallejas | 0.1629 | 1 | 1d 4h ago |
| 22 | Scotty77 | 0.1590 | 5 | 3d 7h ago |
| 23 | fishnchips | 0.1587 | 7 | 4d 21h ago |
| 24 | extradr19 | 0.1563 | 2 | 1d 18h ago |
| 25 | SDCF9 | 0.1563 | 2 | 35min ago |
| 26 | smashi34 | 0.1560 | 1 | 1d ago |
| 27 | hudsonenterprises | 0.1543 | 4 | 1d 7h ago |
| 28 | Aero | 0.1500 | 5 | 1w 1d ago |
| 29 | GeoTrace | 0.1498 | 6 | 1w 2d ago |
| 30 | mlandry | 0.1481 | 5 | 13h 11min ago |
| 31 | Milieunomics | 0.1466 | 10 | 1w 3d ago |
| 32 | kbrodt | 0.1456 | 10 | 6d 22h ago |
| 33 | syntropy-digital | 0.1433 | 5 | 4d 18h ago |
| 34 | Beacon | 0.1407 | 7 | 1w 3d ago |
| 35 | Waltz157 | 0.1403 | 9 | 3d 1h ago |
| 36 | Milieu | 0.1401 | 6 | 1w 3d ago |
| 37 | joano | 0.1350 | 5 | 1w 4d ago |
| 38 | zeaal (vladee, ahome) | 0.1350 | 12 | 1w 4d ago |
| 39 | jorgeschmidt | 0.1256 | 9 | 1w 3d ago |
| 40 | mtrpdx | 0.1219 | 7 | 5d 2h ago |
| 41 | smrtdoog5 | 0.1193 | 1 | 1d ago |
| 42 | ahkarl13 | 0.1148 | 6 | 1w 5d ago |
| 43 | DBbun (kartoun) | 0.1119 | 3 | 1w 4d ago |
| 44 | mctamro | 0.1007 | 2 | 5d 4h ago |
| 45 | lfiaschi | 0.0982 | 2 | 5d 6h ago |
| 46 | finding_true_north | 0.0966 | 4 | 1w 1d ago |
| 47 | dreanarc | 0.0926 | 4 | 3d 13h ago |
| 48 | ganesh_stemx | 0.0902 | 7 | 5h 8min ago |
| 49 | tarabird90 | 0.0878 | 4 | 5d 23h ago |
| 50 | wbg1 | 0.0830 | 2 | 1d ago |

Notes taken while reading (not from the table):

* The page renders the board client-side; the fetcher returned the table rows and a
  trailing `Loading...` fragment, so 50 rows is all that was visible.
* Team rows 13 and 38 list two member accounts; the brief's five numbers are
  single-account rows.
* No row on this board is attributable to this workspace. There is no evidence
  connecting any DrivenData account here to the `buffedlizard55-lab` GitHub
  account, and none is assumed.
