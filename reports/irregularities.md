# Irregularities for review

Generated: 2026-09-23T11:48:54Z

This file is produced by the audit stage. It lists everything the engine could not
reconcile on its own. Nothing here is a conclusion; each entry is a request for a human
decision, with the evidence needed to make it.

**Totals (open)** - error: 0, warning: 17, info: 25; resolved by a reviewer: 8 (error: 1, warning: 0, info: 7).

## Stage: audit

### [ERROR] Generated summary contains figures not present in any verified claim

- **id:** `irr-d5ae8a348d92`
- **topic:** n/a
- **detail:** Figures: 9309
- **suggested action:** Remove the figure or add a verified claim that supports it.
- **detected:** 2026-09-23T00:44:39Z
- **resolved by a reviewer:** 2026-09-23T00:46:00Z
- **reviewer's reason:** The generated summary quoted the standard's document number (RFC 9309) in a sentence about the access-policy gate. The narrative guard is right to reject it: every figure in a generated sentence must be a measured figure or come from a verified claim, and a document number is neither. The sentence was reworded to say 'the access-policy gate' and the RFC number is published, linked, on the sources page and in docs/SOURCES.md instead.

### [WARNING] 1 source(s) were not reachable during this run

- **id:** `irr-c7702daed02e`
- **topic:** n/a
- **detail:** Unavailable sources: github
- **suggested action:** Confirm network egress from the runner, or accept snapshot replay for these sources.
- **detected:** 2026-09-23T00:48:52Z

### [WARNING] 5 source(s) were not reachable during this run

- **id:** `irr-7a8a2e69fe6e`
- **topic:** n/a
- **detail:** Unavailable sources: arxiv, crossref, hackernews, openalex, semantic_scholar
- **suggested action:** Confirm network egress from the runner, or accept snapshot replay for these sources.
- **detected:** 2026-09-22T00:22:28Z

### [WARNING] Topic 'Activity adoption signal' produced no verified claims

- **id:** `irr-bb461e738371`
- **topic:** topic-26bc17638c81
- **detail:** Either every source failed, or the retrieved documents did not contain quotable content.
- **suggested action:** Check the source status table for this topic and add or repair sources.
- **detected:** 2026-09-21T23:55:00Z

### [WARNING] Topic 'Adoption signal' produced no verified claims

- **id:** `irr-d30052aa6bb1`
- **topic:** topic-33df4650da1c
- **detail:** Either every source failed, or the retrieved documents did not contain quotable content.
- **suggested action:** Check the source status table for this topic and add or repair sources.
- **detected:** 2026-09-21T23:55:00Z

### [WARNING] Topic 'Below names' produced no verified claims

- **id:** `irr-073635cdbf14`
- **topic:** topic-de98c08d2b68
- **detail:** Either every source failed, or the retrieved documents did not contain quotable content.
- **suggested action:** Check the source status table for this topic and add or repair sources.
- **detected:** 2026-09-21T23:55:00Z

### [WARNING] Topic 'Every sentence below names' produced no verified claims

- **id:** `irr-5e5c256f577a`
- **topic:** topic-73743b7627fa
- **detail:** Either every source failed, or the retrieved documents did not contain quotable content.
- **suggested action:** Check the source status table for this topic and add or repair sources.
- **detected:** 2026-09-21T23:55:00Z

### [WARNING] Topic 'Every sentence below' produced no verified claims

- **id:** `irr-149c68aed9e5`
- **topic:** topic-775b28699cff
- **detail:** Either every source failed, or the retrieved documents did not contain quotable content.
- **suggested action:** Check the source status table for this topic and add or repair sources.
- **detected:** 2026-09-21T23:55:00Z

### [WARNING] Topic 'Sentence below names' produced no verified claims

- **id:** `irr-38ec6402d9cf`
- **topic:** topic-4047a11c4d73
- **detail:** Either every source failed, or the retrieved documents did not contain quotable content.
- **suggested action:** Check the source status table for this topic and add or repair sources.
- **detected:** 2026-09-21T23:55:00Z

### [WARNING] Topic 'Sentence below' produced no verified claims

- **id:** `irr-7b401468d982`
- **topic:** topic-3f1faf16146a
- **detail:** Either every source failed, or the retrieved documents did not contain quotable content.
- **suggested action:** Check the source status table for this topic and add or repair sources.
- **detected:** 2026-09-21T23:55:00Z

## Stage: change_scan

### [WARNING] Change scan could not reach arxiv

- **id:** `irr-43ca699ef8b8`
- **topic:** n/a
- **detail:** export.arxiv.org unreachable: TLS/SSL connection has been closed (EOF) (_ssl.c:992). The window 2026-09-15..2026-09-22 was not polled, so items published in it will appear as new on a later run rather than being missed.
- **suggested action:** Re-run the scan from a host with egress to this source.
- **detected:** 2026-09-22T00:22:28Z

### [WARNING] Change scan could not reach crossref

- **id:** `irr-8268b26e8ebc`
- **topic:** n/a
- **detail:** api.crossref.org unreachable: TLS/SSL connection has been closed (EOF) (_ssl.c:992). The window 2026-09-15..2026-09-22 was not polled, so items published in it will appear as new on a later run rather than being missed.
- **suggested action:** Re-run the scan from a host with egress to this source.
- **detected:** 2026-09-22T00:22:28Z

### [WARNING] Change scan could not reach nvd

- **id:** `irr-0f32c8d0a71f`
- **topic:** n/a
- **detail:** services.nvd.nist.gov unreachable: TLS/SSL connection has been closed (EOF) (_ssl.c:992). The window 2026-09-15..2026-09-22 was not polled, so items published in it will appear as new on a later run rather than being missed.
- **suggested action:** Re-run the scan from a host with egress to this source.
- **detected:** 2026-09-22T00:22:28Z

### [WARNING] Change scan could not reach usgs_earthquake

- **id:** `irr-b9fce9a77ea5`
- **topic:** n/a
- **detail:** earthquake.usgs.gov unreachable: TLS/SSL connection has been closed (EOF) (_ssl.c:992). The window 2026-09-15..2026-09-22 was not polled, so items published in it will appear as new on a later run rather than being missed.
- **suggested action:** Re-run the scan from a host with egress to this source.
- **detected:** 2026-09-22T00:22:28Z

### [WARNING] Change scan for arxiv returned HTTP 406

- **id:** `irr-c14cbd18b617`
- **topic:** n/a
- **link:** <https://info.arxiv.org/help/api/user-manual.html>
- **detail:** Request: https://export.arxiv.org/api/query with {"max_results": 5, "search_query": "all:autonomous agent", "sortBy": "submittedDate", "sortOrder": "descending", "start": 0}. Response: 
- **suggested action:** Verify the filter against the source's documentation and update changes.py.
- **detected:** 2026-09-22T21:25:05Z

### [WARNING] Change scan for arxiv was refused by the operator's robots.txt

- **id:** `irr-e8c882a22d3f`
- **topic:** n/a
- **link:** <https://export.arxiv.org/robots.txt>
- **detail:** https://export.arxiv.org/robots.txt answered HTTP 200 with content-type text/html; charset=utf-8, not the text/plain that RFC 9309 2.3 requires. The body was parsed anyway: whatever rules it contains are followed, and if it contains none, no rules apply. disallow rule 'Disallow: . The window 2026-09-16..2026-09-23 was not polled for this source.
- **suggested action:** Register a route the operator's own rules permit, or leave the source unscanned.
- **detected:** 2026-09-23T11:48:47Z

### [WARNING] Change scan for nvd returned HTTP 404

- **id:** `irr-b52f25d10d39`
- **topic:** n/a
- **link:** <https://nvd.nist.gov/developers/vulnerabilities>
- **detail:** Request: https://services.nvd.nist.gov/rest/json/cves/2.0 with {"keywordSearch": "autonomous agent", "lastModEndDate": "2026-09-22T00:00:00:000 UTC-00:00", "lastModStartDate": "2026-09-15T00:00:00:000 UTC-00:00", "resultsPerPage": 5}. Response: 
- **suggested action:** Verify the filter against the source's documentation and update changes.py.
- **detected:** 2026-09-22T21:25:06Z

## Stage: policy

### [WARNING] arxiv not requested: robots.txt disallows the path

- **id:** `irr-2dbd1c79ac00`
- **topic:** topic-fabrication-detection
- **link:** <https://export.arxiv.org/robots.txt>
- **detail:** robots.txt rule 'Disallow: /' disallows /api/query; https://export.arxiv.org/robots.txt answered HTTP 200 with content-type text/html; charset=utf-8, not the text/plain that RFC 9309 2.3 requires. The body was parsed anyway: whatever rules it contains are followed, and if it contains none, no rules 
- **suggested action:** Read the operator's robots.txt and API documentation; the engine obeys RFC 9309 and does not work around a disallow rule. If the operator documents the route for API consumers, a reviewer can register a route the operator's own rules permit.
- **detected:** 2026-09-23T11:48:38Z

## Stage: audit

### [INFO] 24 stored claim(s) are marked superseded and are excluded from re-verification

- **id:** `irr-569286381eaf`
- **topic:** n/a
- **detail:** A superseded claim is one a later cycle no longer produces. It remains in the library with the reason recorded on it, and is not published as a current finding.
- **suggested action:** Nothing to do unless a reviewer believes a retired statement was correct.
- **detected:** 2026-09-22T21:25:06Z

### [INFO] 4 library-statistic statement(s) retired for topic-autonomous-research-agents

- **id:** `irr-c0fc2312c838`
- **topic:** topic-autonomous-research-agents
- **detail:** A re-run of the library statistics produced different figures, so the previous "currently supported by ..." statements are marked superseded. The records remain in library/claims.jsonl with the reason stored on each, and the pages publish only the current figures.
- **suggested action:** Nothing to do unless a reviewer believes the old figures were correct.
- **detected:** 2026-09-22T22:03:24Z

### [INFO] 4 library-statistic statement(s) retired for topic-fabrication-detection

- **id:** `irr-efcc377db02b`
- **topic:** topic-fabrication-detection
- **detail:** A re-run of the library statistics produced different figures, so the previous "currently supported by ..." statements are marked superseded. The records remain in library/claims.jsonl with the reason stored on each, and the pages publish only the current figures.
- **suggested action:** Nothing to do unless a reviewer believes the old figures were correct.
- **detected:** 2026-09-22T22:03:25Z

### [INFO] 4 library-statistic statement(s) retired for topic-research-loop-scheduling

- **id:** `irr-a3f3cdf7cce5`
- **topic:** topic-research-loop-scheduling
- **detail:** A re-run of the library statistics produced different figures, so the previous "currently supported by ..." statements are marked superseded. The records remain in library/claims.jsonl with the reason stored on each, and the pages publish only the current figures.
- **suggested action:** Nothing to do unless a reviewer believes the old figures were correct.
- **detected:** 2026-09-22T22:03:25Z

### [INFO] 4 library-statistic statement(s) retired for topic-search-and-sorting-strategy

- **id:** `irr-d8825881157a`
- **topic:** topic-search-and-sorting-strategy
- **detail:** A re-run of the library statistics produced different figures, so the previous "currently supported by ..." statements are marked superseded. The records remain in library/claims.jsonl with the reason stored on each, and the pages publish only the current figures.
- **suggested action:** Nothing to do unless a reviewer believes the old figures were correct.
- **detected:** 2026-09-22T22:03:27Z

### [INFO] Stored claims are marked superseded and are excluded from re-verification

- **id:** `irr-6218b1a3c625`
- **topic:** n/a
- **detail:** 134 claim(s) currently carry a supersession reason. A superseded claim is one a later cycle no longer produces. It remains in the library with the reason recorded on it, and is not published as a current finding.
- **suggested action:** Nothing to do unless a reviewer believes a retired statement was correct.
- **detected:** 2026-09-23T11:48:53Z

## Stage: change_scan

### [INFO] Change scan for arxiv was refused by the operator's robots.txt

- **id:** `irr-4bc3891da960`
- **topic:** n/a
- **link:** <https://export.arxiv.org/robots.txt>
- **detail:** https://export.arxiv.org/robots.txt could not be fetched (URLError: <urlopen error TLS/SSL connection has been closed (EOF) (_ssl.c:992)>). RFC 9309 2.3.1.4: an unreachable robots.txt means the file is undefined and a crawler MUST assume complete disallow, so no request was made . The window 2026-09-16..2026-09-23 was not polled for this source.
- **suggested action:** Register a route the operator's own rules permit, or leave the source unscanned.
- **detected:** 2026-09-23T00:55:16Z

### [INFO] Change scan for crossref was refused by the operator's robots.txt

- **id:** `irr-159938997d12`
- **topic:** n/a
- **link:** <https://api.crossref.org/robots.txt>
- **detail:** https://api.crossref.org/robots.txt could not be fetched (URLError: <urlopen error TLS/SSL connection has been closed (EOF) (_ssl.c:992)>). RFC 9309 2.3.1.4: an unreachable robots.txt means the file is undefined and a crawler MUST assume complete disallow, so no request was made . The window 2026-09-22..2026-09-23 was not polled for this source.
- **suggested action:** Register a route the operator's own rules permit, or leave the source unscanned.
- **detected:** 2026-09-23T00:55:16Z

### [INFO] Change scan for nvd was refused by the operator's robots.txt

- **id:** `irr-147cd6c3b572`
- **topic:** n/a
- **link:** <https://services.nvd.nist.gov/robots.txt>
- **detail:** https://services.nvd.nist.gov/robots.txt could not be fetched (URLError: <urlopen error TLS/SSL connection has been closed (EOF) (_ssl.c:992)>). RFC 9309 2.3.1.4: an unreachable robots.txt means the file is undefined and a crawler MUST assume complete disallow, so no request was . The window 2026-09-16..2026-09-23 was not polled for this source.
- **suggested action:** Register a route the operator's own rules permit, or leave the source unscanned.
- **detected:** 2026-09-23T00:55:16Z

### [INFO] Change scan for usgs_earthquake was refused by the operator's robots.txt

- **id:** `irr-32f4f0d4ade9`
- **topic:** n/a
- **link:** <https://earthquake.usgs.gov/robots.txt>
- **detail:** https://earthquake.usgs.gov/robots.txt could not be fetched (URLError: <urlopen error TLS/SSL connection has been closed (EOF) (_ssl.c:992)>). RFC 9309 2.3.1.4: an unreachable robots.txt means the file is undefined and a crawler MUST assume complete disallow, so no request was ma. The window 2026-09-22..2026-09-23 was not polled for this source.
- **suggested action:** Register a route the operator's own rules permit, or leave the source unscanned.
- **detected:** 2026-09-23T00:55:16Z

## Stage: policy

### [INFO] hackernews not requested: robots.txt unreachable

- **id:** `irr-6524b709eebd`
- **topic:** topic-autonomous-research-agents
- **link:** <https://hn.algolia.com/robots.txt>
- **detail:** https://hn.algolia.com/robots.txt could not be fetched (URLError: <urlopen error TLS/SSL connection has been closed (EOF) (_ssl.c:992)>). RFC 9309 2.3.1.4: an unreachable robots.txt means the file is undefined and a crawler MUST assume complete disallow, so no request was made to this host.
- **suggested action:** Re-run from a host that can read this operator's robots.txt (RFC 9309 2.3.1.4 requires complete disallow while it is unreachable).
- **detected:** 2026-09-23T00:55:15Z

## Stage: review

### [INFO] Topic topic-26bc17638c81 rejected by a reviewer

- **id:** `irr-0e75bba705aa`
- **topic:** topic-26bc17638c81
- **detail:** Proposed from the engine's own rendering scaffolding, not from subject matter: the phrase recurs in every retrieved document because the adapter writes it, so it is not novel. Fixed in selflearn/think/invention.py by stripping scaffolding before candidate extraction.
- **suggested action:** The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.
- **detected:** 2026-09-21T23:55:57Z
- **resolved by a reviewer:** date not recorded

### [INFO] Topic topic-33df4650da1c rejected by a reviewer

- **id:** `irr-00276c63999a`
- **topic:** topic-33df4650da1c
- **detail:** Proposed from the engine's own rendering scaffolding, not from subject matter: the phrase recurs in every retrieved document because the adapter writes it, so it is not novel. Fixed in selflearn/think/invention.py by stripping scaffolding before candidate extraction.
- **suggested action:** The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.
- **detected:** 2026-09-21T23:55:57Z
- **resolved by a reviewer:** date not recorded

### [INFO] Topic topic-3f1faf16146a rejected by a reviewer

- **id:** `irr-64d0b7776639`
- **topic:** topic-3f1faf16146a
- **detail:** Proposed from the engine's own rendering scaffolding, not from subject matter: the phrase recurs in every retrieved document because the adapter writes it, so it is not novel. Fixed in selflearn/think/invention.py by stripping scaffolding before candidate extraction.
- **suggested action:** The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.
- **detected:** 2026-09-21T23:55:57Z
- **resolved by a reviewer:** date not recorded

### [INFO] Topic topic-4047a11c4d73 rejected by a reviewer

- **id:** `irr-8638b3cc17d7`
- **topic:** topic-4047a11c4d73
- **detail:** Proposed from the engine's own rendering scaffolding, not from subject matter: the phrase recurs in every retrieved document because the adapter writes it, so it is not novel. Fixed in selflearn/think/invention.py by stripping scaffolding before candidate extraction.
- **suggested action:** The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.
- **detected:** 2026-09-21T23:55:57Z
- **resolved by a reviewer:** date not recorded

### [INFO] Topic topic-73743b7627fa rejected by a reviewer

- **id:** `irr-0fcd91bbd590`
- **topic:** topic-73743b7627fa
- **detail:** Proposed from the engine's own rendering scaffolding, not from subject matter: the phrase recurs in every retrieved document because the adapter writes it, so it is not novel. Fixed in selflearn/think/invention.py by stripping scaffolding before candidate extraction.
- **suggested action:** The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.
- **detected:** 2026-09-21T23:55:57Z
- **resolved by a reviewer:** date not recorded

### [INFO] Topic topic-775b28699cff rejected by a reviewer

- **id:** `irr-bf5855534bb7`
- **topic:** topic-775b28699cff
- **detail:** Proposed from the engine's own rendering scaffolding, not from subject matter: the phrase recurs in every retrieved document because the adapter writes it, so it is not novel. Fixed in selflearn/think/invention.py by stripping scaffolding before candidate extraction.
- **suggested action:** The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.
- **detected:** 2026-09-21T23:55:57Z
- **resolved by a reviewer:** date not recorded

### [INFO] Topic topic-de98c08d2b68 rejected by a reviewer

- **id:** `irr-aabcbed375e6`
- **topic:** topic-de98c08d2b68
- **detail:** Proposed from the engine's own rendering scaffolding, not from subject matter: the phrase recurs in every retrieved document because the adapter writes it, so it is not novel. Fixed in selflearn/think/invention.py by stripping scaffolding before candidate extraction.
- **suggested action:** The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.
- **detected:** 2026-09-21T23:55:57Z
- **resolved by a reviewer:** date not recorded

## Stage: synthesis

### [INFO] 0 brief(s), 0 criticism(s) and 1 open question(s) withdrawn with their retired claims

- **id:** `irr-2bc1e095b18b`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-23T00:55:16Z

### [INFO] 0 brief(s), 0 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-0408a7003b12`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-23T04:53:10Z

### [INFO] 0 brief(s), 0 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-29e94b8d954c`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-23T00:42:16Z

### [INFO] 0 brief(s), 0 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-5a6a81604c30`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-23T00:44:39Z

### [INFO] 0 brief(s), 0 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-648fdbd55f2a`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-22T23:12:31Z

### [INFO] 0 brief(s), 0 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-6b9ba9d4bde9`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-23T00:46:12Z

### [INFO] 0 brief(s), 0 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-b59992f5dcf9`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-23T11:48:50Z

### [INFO] 0 brief(s), 0 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-f9e51e2c06d5`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-23T00:48:52Z

### [INFO] 109 brief(s), 449 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-bb345a59eabf`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-22T21:44:30Z

### [INFO] 21 brief(s), 83 criticism(s) and 3 open question(s) withdrawn with their retired claims

- **id:** `irr-a2b19bc8ff0e`
- **topic:** n/a
- **detail:** These records quote a claim that a later cycle no longer produces. They stay in the library with the reason recorded on each, and are excluded from the competing answers, criticisms and open questions on the published pages.
- **suggested action:** Review the retired statements section on the affected topic pages.
- **detected:** 2026-09-22T22:03:28Z

### [INFO] 6 cross-document statement(s) retired for topic-autonomous-research-agents

- **id:** `irr-9eedabcee374`
- **topic:** topic-autonomous-research-agents
- **detail:** The synthesis rules no longer produce these statements, so they are marked superseded and are not published as current findings. The records remain in library/claims.jsonl with the reason stored on each.
- **suggested action:** No action needed unless a reviewer believes a retired statement was correct.
- **detected:** 2026-09-22T00:08:00Z

### [INFO] 6 cross-document statement(s) retired for topic-fabrication-detection

- **id:** `irr-d1fed35636e8`
- **topic:** topic-fabrication-detection
- **detail:** The synthesis rules no longer produce these statements, so they are marked superseded and are not published as current findings. The records remain in library/claims.jsonl with the reason stored on each.
- **suggested action:** No action needed unless a reviewer believes a retired statement was correct.
- **detected:** 2026-09-22T00:08:01Z

### [INFO] 6 cross-document statement(s) retired for topic-research-loop-scheduling

- **id:** `irr-6fed4ba31f00`
- **topic:** topic-research-loop-scheduling
- **detail:** The synthesis rules no longer produce these statements, so they are marked superseded and are not published as current findings. The records remain in library/claims.jsonl with the reason stored on each.
- **suggested action:** No action needed unless a reviewer believes a retired statement was correct.
- **detected:** 2026-09-22T00:08:02Z

### [INFO] 6 cross-document statement(s) retired for topic-search-and-sorting-strategy

- **id:** `irr-9c1dc4f51574`
- **topic:** topic-search-and-sorting-strategy
- **detail:** The synthesis rules no longer produce these statements, so they are marked superseded and are not published as current findings. The records remain in library/claims.jsonl with the reason stored on each.
- **suggested action:** No action needed unless a reviewer believes a retired statement was correct.
- **detected:** 2026-09-22T00:08:04Z
