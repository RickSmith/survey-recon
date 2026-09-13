# TxDOT ROW Survey — Source Material & Verified Endpoints

Research compiled 2026-09-12. Test corridor throughout: SH16 / Bandera Rd, Loop 410 → Gibeaut Rd, Bexar County. Bbox `-98.66,29.45,-98.56,29.56` (WGS84), midpoint `29.505,-98.615`.

---

## PART 1 — The control spike, largely pre-completed

All of the following were **queried live and returned real results**.

| Query | Result |
|---|---|
| NGS marks within 2 mi of corridor midpoint | **13 marks**, several flagged `MARK NOT FOUND` |
| TxDOT Primary Control Points in corridor | **18** (376 in Bexar, 766 statewide) |
| TxDOT ROW map sheets for SH16 in Bexar | **27 sheets, 1937–1998, across 3 control sections** |
| BCAD parcels in corridor bbox | ~55,000 (needs alignment buffer, not bbox) |
| USGS quads covering corridor | 4, with direct geoPDF download links |
| USGS cemeteries in corridor | 5 |

### Verified endpoints

**TxDOT** — AGOL org `KTcxiTD9dsQw4r7Z`, base `https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/<name>/FeatureServer`

| Service | Layer | Notes |
|---|---|---|
| `Primary_Control_Points` | **67** | `NGS_PERM_ID`, `MONUMENT_STAMPING_TXT`, `MONUMENT_COND_DSCR`, `MONUMENT_STBL_CD`, `HRZNTL_DATUM_NM`, `VERT_DATUM_NM`, `STATE_PLN_ZN_NM`, `STATN_COMBN_SCL_FCTR_MS`, `LAST_RCOV_DT`, `SRVY_CTRL_DCMNT_ADDR` (PDF link), `INTERVSBL_STATN_NM`. WKID 103161 — pass `outSR=4326` |
| `Roadway_Inventory_2023` | 0 | 214 fields incl. **`ROW_MIN`** (existing ROW width), `NUM_LANES`, `ADT_CUR` |
| `TxDOT_Roadways` | 0 | `RTE_NM`, `BEGIN_DFO`/`END_DFO` linear referencing |
| `ROW_ODP_Proposed_Parcels` | 0 | Proposed acquisition parcels |
| `RPAM_ODP_Access_Control_Lines` | 0 | Denial of access |
| `2025_Land_Parcels` | **328** | TxDOT-owned land |
| `_District_Survey_Coordinators` | 0 | Who to call per district |

**Discovery method that works:** `https://www.arcgis.com/sharing/rest/search?q=orgid:KTcxiTD9dsQw4r7Z+AND+<terms>&num=100&f=pjson` (313 items). The Hub DCAT feed only exposes 26.

**Layer IDs are frequently NOT 0** (control = 67, land parcels = 328). An agent that hardcodes `/FeatureServer/0` fails silently. Always read `FeatureServer?f=json` first. *Good teaching moment.*

!!! warning "Corrected 2026-09-12, while building [#15](https://github.com/RickSmith/survey-recon/issues/15)"
    Four claims on this page about `Primary_Control_Points` did not survive being
    queried. The full account is on [the TxDOT control points
    page](data-sources/txdot-control-points.md); in short:

    1. **"An agent that hardcodes `/FeatureServer/0` fails silently" is not true
       of either service named.** Both `Primary_Control_Points` and
       `2025_Land_Parcels` answer a request for layer 0 with `HTTP 400 — The
       requested layer was not found`, because on each the numbered layer is the
       only layer there is. The quiet wrong answer is a *different service*:
       `TxDOT_Control_Sections/FeatureServer/0` exists, answers without erroring,
       and holds numbered highway segments rather than monuments. Still a good
       teaching moment — a better one — but not the one written here.
    2. **`SRVY_CTRL_DCMNT_ADDR` is not a PDF link.** It is null on all 766
       records. The control sheets are ArcGIS *attachments*; `queryAttachments`
       resolves them.
    3. **"766 statewide" is the record count, not the coverage.** The service's
       own title is *San Antonio District* Primary Control Points, and 715 of the
       766 records are in district 15.
    4. **766 records carry only 492 distinct station names.** 274 stations appear
       twice. A count of records is not a count of monuments.

    The `outSR=4326` note was right and is load-bearing.

**TxDOT ROW map index — the standout find**
```
https://maps.dot.state.tx.us/arcgis/rest/services/ROW/ROW_Maps_CL_2017/MapServer/0
```
ROW map sheets **are** geospatially indexed. Fields: `MAP_NM`, `ROW_MAP_ID`, `CTRL_SECT_NBR`, `CSJ_NBR`, `RTE_NM`, `CNTY_NM`, `MAP_LMT_FROM_DSCR`/`TO`, `TOTL_MAP_PAGE_QTY`, `MAP_FROM_DT`/`TO_DT`. Naming = `District-ControlSection-Route-MapDate`, e.g. `SAT-029110-SH0016-19980306`. SH16 Bexar control sections: 0291-09, 0291-10, 0613-01.
**Caveat:** no field gives a direct PDF URL. You get the sheet count and IDs; the documents still come through ROW Division or the RPAM viewer.

**NGS** — base `https://geodesy.noaa.gov/api/nde/`

| Endpoint | Params |
|---|---|
| `/radial` | `lat`, `lon`, `radius`, `units` (MILE default) |
| `/bounds` | `minlat`, `maxlat`, `minlon`, `maxlon` |
| `/pid` | `pid` (comma-delimited) |
| `/meta` | parameter definitions |

500-record cap. Returns `pid`, `stamping`, `monumentType`, `setting`, `stability`, **`condition`**, `lastRecovered`, `posDatum`, `posOrder`, `vertDatum`, `vertOrder`, `orthoHt`, `ellipHeight`, `geoidHt`, `geoidModel`, `spcZone`, `spcNorthing`/`Easting`, `corsId`, `pacsSacs` — 44 fields.

Better for corridor polygons (arbitrary geometry + pagination, 2000 max):
```
https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/NGS_Datasheets_Feature_Service/FeatureServer/1
```
54 marks in corridor bbox. Field names differ from the NDE API.

**Parcels**

| Source | Endpoint | Refresh |
|---|---|---|
| CoSA → BCAD *(preferred)* | `https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/BCAD_Parcels/FeatureServer/0` | **Weekly** |
| Bexar County | `https://maps.bexar.org/arcgis/rest/services/Parcels/MapServer/0` | Annual Sept/Oct |
| CoSA own server | `gis.sanantonio.gov/arcgis/rest/services` | **Empty — avoid** |

Fields, **by service** — the two do not share field names:

| Service | Fields |
|---|---|
| CoSA → BCAD *(preferred)* | `Geo_id`, `PropID`, `Situs`, `Owner_Name`, `legal_desc`, `legal_acre`, `state_cd`, `addr_line1`–`3`, `addr_city`, `zip`, `Exemptions`, `neighborho`, `GBA_Living`, `ParcelArea`, `LandSqft` |
| Bexar County | `Owner`, `Situs`, `AcctNumb`, `LglDesc`, `LglAcres`, `LandVal`, `ImprVal`, `TotVal`, `PropUse`, `Acres`, `YrBlt`, `State_cd` |

CoSA AGOL also has `RecordedPlat`, `PreliminaryPlat`, `Major_Thoroughfare_Plan__MTP` as separate layers.

!!! warning "Corrected 2026-09-12"
    This line previously gave the Bexar County field list — `AcctNumb`, `Owner`,
    `LglDesc`, `LglAcres`, `PropUse` — as the fields of the **CoSA** service. Both
    lists are real; they were attached to the wrong endpoints. Both services were
    read again on 2026-09-12 while building the corridor tool, and the table above
    is what each one actually publishes.

    It matters because the preferred service is the CoSA one, and a query asking
    it for `AcctNumb` fails outright. That is the good case. The bad case is the
    one this repo keeps warning about: a field list that is wrong in a way the
    server answers anyway. `State_cd` exists on Bexar County and `state_cd` on
    CoSA, differing only in one capital letter.

    [Spec section 10](corridor-screen/spec.md) named `AcctNumb` as the parcel
    identifier. It was left alone until Rick ruled on it, because the spec is a
    settled contract and amending one is not the agent's call. He ruled on
    2026-09-13, on [PR #52](https://github.com/RickSmith/survey-recon/pull/52),
    and section 10 now carries the real field names with a note recording the
    amendment. The tool follows the service either way, and the mapping lives in
    `corridor-screen/corridor_screen/sources.py`.

**Ancillary — USGS `carto.nationalmap.gov` covers most of the list from one server**
```
/arcgis/rest/services/structures/MapServer
   2 Cemeteries · 14 Hospitals · 15 Ambulance · 16 Fire/EMS · 23 Schools · 11 Historic Sites
/arcgis/rest/services/transportation/MapServer
  38 Railroads
```
Also: Bexar railroads/schools/school-districts MapServers · CoSA Cemetery Steward Program · ~~NPMS pipelines (`services.arcgis.com/G4S1dGvn7PIgYd6Y/.../NPMS_Pipelines_2022`)~~ — **see the correction below** · USGS TNM Access API for quads.

!!! danger "Corrected 2026-09-12, while building [issue #17](https://github.com/RickSmith/survey-recon/issues/17)"
    **`NPMS_Pipelines_2022` holds no Texas data.** NPMS is the National Pipeline
    Mapping System, run by the federal Pipeline and Hazardous Materials Safety
    Administration. Read live: 543 records in
    total, **zero** in Texas, zero in Bexar County, and every sample record in
    **Chester County, Pennsylvania**. The layer's own extent sits around
    longitude −76, latitude 40.

    A Texas query returns zero records and no error, which reads exactly like
    "there are no pipelines here."

    This is the same trap recorded three rows below in this very table, for
    `FEMA_Flood_Zones` on services9 — *"ranks high in search but is Salem, MA
    only. Easy trap."* This research fell into its own documented trap a second
    time, and the only reason it was caught is that a corridor with zero
    pipelines looked odd enough to check the county, and then the state.

    **The source used instead** is the **Texas Pipeline Mapping System (TPMS)**
    from the Railroad Commission of Texas —
    `gis.rrc.texas.gov/server/rest/services/rrc_public/tpms/MapServer/0`.
    490,375 records, 598 within a box around Bexar County, and a genuine zero
    inside the SH16 corridor. Full write-up in
    [the flag services page](data-sources/flag-services.md).

    Correcting a settled spec is not the agent's call, so it was raised on
    [PR #53](https://github.com/RickSmith/survey-recon/pull/53) — the same route
    the parcel field names took on
    [PR #52](https://github.com/RickSmith/survey-recon/pull/52). Rick ruled on
    2026-09-13, and [spec section 6](corridor-screen/spec.md) now names TPMS.

    The line in the table above is struck through rather than deleted. This
    research note is the record of what was believed on 2026-09-12, and a record
    that quietly edits out its own wrong turns is not a record.

!!! warning "Also found 2026-09-12 — the USGS structures buffer answers for the wrong county"
    Asked with the SH16 Bexar **polyline and a distance**, `structures` layer 23
    returned schools in **Kerrville and Fredericksburg**, sixty miles up SH16,
    for a query whose geometry stopped inside Bexar County. No error. Thinning
    the line to 90 vertices did not fix it; an envelope was correct every time.

    That is a third example of the 3DEP failure pattern — a parameter quietly
    ignored, a plausible answer returned. The corridor tool asks the flag
    services with an envelope because of it, and checks their answers anyway.
    Tables and test numbers in
    [the flag services page](data-sources/flag-services.md).

### Demo risk

| Risk | Detail |
|---|---|
| **`maps.dot.state.tx.us` robots.txt intermittent** | Same URL failed then succeeded minutes later. Most impressive find **and** riskiest. **Cache the 27-sheet result.** |
| **USGS 3DEP `identify` / EPQS elevation** | Timed out 3 of 4 attempts. Keep off the critical path. |
| **FEMA NFHL robots-blocked** | Use Esri Living Atlas `USA_Flood_Hazard_Reduced_Set` instead (250-record cap). |
| **`FEMA_Flood_Zones` on services9** | Ranks high in search but is **Salem, MA only**. Easy trap. |
| **3DEP silently returned `NoData`** | Ignored `sr=4326`, read lon/lat as Web Mercator meters. Returned a plausible non-answer rather than an error. |

---

## PART 2 — TxDOT rules an agent can read

### Survey Manual (ESS), rev. April 2026 — https://www.txdot.gov/manuals/row/ess/index.html
Only five chapters. **The manual is thin; the binding numbers live in the toolkit documents it references** and in ROW Preliminary Procedures Ch. 4.

**Prescriptive, Ch. 3 (Control Points):**
- Primary control tied to NSRS, "not more than approximately three (3) miles apart," **intervisible pairs**, Level 2A, recorded on ROW-S-2462, signed and sealed
- Secondary: Level 3, intervisible at max 1,500 ft
- US Survey Feet in all deliverables; horizontal to 0.01 ft; lat/long DMS to five decimals
- `meters × 3937/1200`, factor to 12 decimals
- **"TxDOT will not accept any datum transformations for control."** NCAT is the only named conversion software
- **"All control coordinates will be provided in surface and grid"** using per-county factors from `surface-adjustment-factors.xlsx`

**Prescriptive, Ch. 4 (Design Surveys) — tolerance table:**

| Feature | Horizontal | Vertical |
|---|---|---|
| Bridges / roadway structures | <0.1 ft | <0.04 ft (0.02 multi-phase) |
| Utilities / improvements | <0.2 ft | <0.1 ft |
| Cross-sections / profiles | <1 ft | <0.2 ft |
| Bore holes | <3 ft | <0.5 ft |

- **"There is no acceptable failure rate for any TxDOT survey."** Non-compliant surveys cannot be invoiced.
- All graphic design survey files in MicroStation ORD.

**GNSS accuracy levels (`tsla.pdf`):**

| Level | Type | Local (95%) | Geodetic | Elev | Max baseline | Occupation |
|---|---|---|---|---|---|---|
| 1 major control densification | Static | 8 mm +1 ppm | 12 mm | 22 mm | 40 mi CORS | 2 hr + 1 min/km, 2 occ. 2 hr apart |
| 2A primary project control | Static | 8 mm +1 ppm | 20 mm | 25 mm | 30 mi CORS / 2 mi pt-pt | 1 hr + 1 min/km, 2 occ. |
| 2B local project control | RTN | 8 mm +1 ppm | 20 mm | 25 mm | 30 mi / 2 mi | 180 epochs, rod rotated 180°, 2 occ. |
| 3 secondary, GCPs, property corners | RTK | 12 mm +1 ppm | 25 mm | 30 mm | 5 mi RTK | 180 epochs, rod rotated 180°, 2 occ. |

All levels require RPLS supervision.

### The datum gap — a genuine finding
The April 2026 Survey Manual names **no NAD83 realization** (no "NAD83(2011)"), **no epoch**, and **no geoid model** (no GEOID18). It contains **no reference to SPCS2022, NATRF2022, or NAPGD2022**. It directs projects to both CORS published values *and* 1993 HARN coordinates — two sentences in tension. The survey control SOP (March 2025) uses "Legacy Mapping Plane" and "New Mapping Plane" **without defining either**.

### The traditional paper ROW map is gone
ROW Preliminary Procedures Ch. 4 §1 covers "Elimination of the Requirement for a Traditional Right of Way Map." Replaced by an **ArcGIS geodatabase** of parcel features plus a **signed-and-sealed property description per parcel**, submittable incrementally.
- `ROW_Parcels_Edits_v2` template; rename to ROW CSJ → `ROW_Parcels_255204041.gdb`
- ~13–14 feature classes: Existing_ROW_Points/Lines/Polygons, Survey_Control_Points, ROW_Centerline, Pipeline Leases, Utilities, Access Control/Denial Lines, Disposition Tracts, ROW_Proposed_Parcels, Parent Tract, Preliminary Proposed ROW
- **Geodatabase XY is geographic lat/long NAD83 decimal degrees, 8+ places** — differs from the survey-side Texas SPC US-survey-feet requirement
- Graphics: native MicroStation DGN. Parcel plats `ROWCSJ_ParcelNumber_PgNumber.dgn`. MRF files in **both surface and grid**
- Property descriptions: sealed, **locked PDF**, must state on-the-ground survey with day/month/year
- Final map uploaded to ROW Division via **OnBase**

### Rules-as-data — the most agent-consumable things TxDOT publishes
`required-feature-table.xlsx` · `survey-linking-codes.xlsx` · `surface-adjustment-factors.xlsx` (per-county) · `row-geodatabase-template.zip` (needs GDAL/arcpy)

### Machine-readability
**Good:** all Survey Manual and PPR Ch. 4 HTML pages (best target by far); `ess.pdf`, `monument-specifications.pdf`, `tsla.pdf`, `survey-control.pdf`, `submission-standards.pdf` — text-layer PDFs, not scans. DOCX checklists parse fine.
**Agent-hostile:** ROW-S-2462 and ROW-S-GrndCntrl are **XDP (Adobe LiveCycle)** forms; DesCheck/LLAcqCheck/LLCntrlCheck are **AEM adaptive forms** with no stable document behind them.
**Link-rot trap:** legacy `onlinemanuals.txdot.gov/txdotmanuals/ess/...` URLs still dominate search results while content moved to `txdot.gov/manuals/row/ess/...`. **An agent scraping from search will confidently cite a superseded revision.** This is a scripted demo in the session.
**Host note:** `ftp.txdot.gov` was blocked in testing; the `ftp.dot.state.tx.us` mirror served identical files.

---

## PART 3 — Right of Entry and lead times

### ROE mechanics — TxDOT Survey Manual Ch. 2 §3
https://www.txdot.gov/manuals/row/ess/surveying_procedures/right_of_entry.html

- Every ROE request **must be documented by written letter**; template in the Surveyors' Toolkit
- **Oral ROE is valid for one day and for the one individual who received it**, recorded in field notes and initialed
- Manual explicitly encourages **remote measurement (lidar, UAS, photogrammetry) to avoid entering private property**
- If ROE cannot be obtained, request a **court order** through ROW Division Survey Section; staff "encouraged to avoid reliance upon court orders"
- **"Safety costs may be budgeted in the case of entry into high-risk areas such as railroads or Department of Criminal Justice property."**

**Forms:** ROE request template (.docx, Surveyors' Toolkit) · env. ROE agreement 020-03-frm · Spanish 020-08-frm · **first** request letter 020-10-tem · **second** request letter 020-11-tem · ROW-S-PrelimSite · ROW-S-JSA (daily job safety analysis) · ROW-S-SI

**TxDOT ships a *second* ROE letter template — non-response is the designed-for baseline.**

**No published ROE turnaround exists** in any manual read. The 30-day windows in the acquisition process are offer-stage, not ROE.

### Texas access statute — no self-executing right
- **Tex. Occ. Code § 1071.3585** — an RPLS denied permission **"may seek a court order"**; district court in the county; court **shall** grant on proof of RPLS status **and** that issuance "is in the public's best interest"
- **Tex. Occ. Code § 1071.358** — an **LSLS** in official capacity **"is entitled to"** an order; the **Attorney General** must promptly apply
- No notice-only entry right, no bond, no self-help, no damage immunity
- Condemnor's common-law entry right is limited to **visual inspection and lineal surveys** — no core drilling (*I.P. Farms v. Exxon Pipeline*, 646 S.W.2d 544; *Coastal Marine v. Port Neches*, 11 S.W.3d 509)
- **Penal Code § 30.05** trespass notice includes fencing to contain livestock, cultivated crops, and **purple paint**; **Class A** for critical infrastructure

### Lead-time table — the estimating payload

| Parcel type | Statutory / procedural driver | Lead time |
|---|---|---|
| **Railroad** | Separate corporate ROE. UP: **$1,545** application + **$500** contractor admin fee, Railroad Protective Liability insurance, flagging, 48 hr notice after execution | **30–45 days** |
| **Cemetery** | **HSC § 711.041** — landowner may set route and hours; outside those hours requires **written notice 14 days in advance**. Discovery of unknown cemetery → **county clerk filing within 10 days** (HSC §711.011). Antiquities Code **NRC §191.093** protects 50+ yr burials on public land | **14 days** |
| **School** | District board approval (monthly meetings). **Educ. Code § 22.0834** background checks where continuing duties + direct student contact; **exempt** if work is physically separated by a **6+ ft barrier** with enforced no-contact policy | Board cycle + badging |
| **Pipeline** | **Util. Code ch. 251** — "excavation" = mechanized equipment disturbing soil **16+ inches**, so hand-driven monuments may fall outside. Notify **14 days to 48 hours** before, excluding weekends/holidays | **48 hr floor**, operator standby varies |
| **Church** | No statute; trustee/vestry/diocese authority, monthly meetings | Board cycle |
| **Federal / tribal** | Special-use permit (USFS, USACE, USFWS, NPS); tribal council + BIA. **Not verified** | Assume months |
| **Gated / ag** | No statute. HOA codes, escorts, gate protocol, livestock, biosecurity | Scheduling friction only |

!!! success "Every row above read back to its source, 2026-09-12, under [issue #17](https://github.com/RickSmith/survey-recon/issues/17)"
    The table above was written from research notes. Before those numbers went
    into a tool that prints them, each was opened and read.

    - **Railroad 30–45 days** now has a public citation it did not have before:
      Union Pacific's own procedures page says *"The normal turn-around time for
      processing applications is now running between 30-45 days,"* and confirms
      the $1,545 application fee —
      <https://www.up.com/real-estate/tempuse/procedures>
    - **Cemetery 14 days** confirmed at **§ 711.041(c)(2)** — *"not later than
      the 14th day before the date the person wishes to visit."* The 10-day
      county clerk filing confirmed at **§ 711.011(a)**
    - **Pipeline 48 hours** confirmed at **§ 251.151(a)**, with the weekend and
      holiday exclusion. The 16-inch excavation definition confirmed at
      **§ 251.002**
    - **School** — **§ 22.0834** confirmed, including the six-foot barrier
      exemption at (a-1)(3). It sets **no number of days**, so the tool records
      "not found" and says where it looked

    `statutes.capitol.texas.gov` is now a JavaScript application. The URLs still
    work in a browser, but a plain fetch returns only the app shell — the
    statute text loads client-side. These readings were done in a browser for
    that reason. Anything that machine-fetches those URLs and reports "section
    not found" is wrong about the section, not about the URL.

    The citations and the wording are in
    [Lead times and their sources](corridor-screen/lead-times.md), and the
    machine-readable copy is `corridor-screen/corridor_screen/lead_times.toml`.

### Traffic control — the crew-cost cliff
**2025 TMUTCD**, effective Jan 18 2026. A conformance revision was in public comment through Sept 13 2026 — TCP requirements are actively changing.

TxDOT publishes **six** standard sheets titled "Traffic Control Plan for Surveying Operations": **TCP(S-1)-08A**, **TCP(S-2)-08A**, **TCP(S-2c)-10**, **TCP(S-3)-08**, **TCP(S-4)-08A** and **TCP(S-5)-08**. All six were pulled by hand on 2026-09-13 and are committed with provenance in [`project-sh16/manual-pulls/`](https://github.com/RickSmith/survey-recon/tree/main/project-sh16/manual-pulls). The full reading, with the plan-view evidence, is [`tcp-s-family.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/manual-pulls/tcp-s-family.md).

**The duration line is one hour, and it is the only line.** All six sheets print the same definitions: *short duration* is work that occupies a location **up to 1 hour**; *short term stationary* is daytime work that holds a location for **more than 1 hour** within a single daylight period.

**What crossing the hour costs depends on which sheet you are on.** That split is the whole cost story, and it is legible only in the drawing — see the correction below.

| Sheet and case | Protective vehicle **drawn** | What the hour does |
|---|---|---|
| **TCP(S-2b)** work in roadway<br>**TCP(S-3a)** right lane closed | **Shadow Vehicle with TMA** — one | Permission to substitute an ordinary work vehicle is granted **"for short duration work"** only (S-2 Note 10, S-3 Note 2). Past the hour the permission lapses and the drawn shadow vehicle stands |
| **TCP(S-3b)** work on centerline | **Two** Shadow Vehicles with TMA | The same, doubled. The most expensive configuration in the family — and the one a centerline retracement lands on |
| **TCP(S-1a/b)** off or on shoulder<br>**TCP(S-2c)** two-lane rural intersection<br>**TCP(S-4a/b)** divided, off right shoulder or in median | Plain work vehicle (S-4b draws two, reducible to one behind a median barrier — S-4 Note 2) | The TMA is an **upgrade you may elect**, never a penalty the clock triggers (S-1 Note 4, S-4 Note 4). Crossing the hour costs the G20-2a "END ROAD WORK" sign and a run of channelizing devices — setup and teardown time, not a second vehicle |
| **TCP(S-2a)** road closed under 20 min | **None** — flaggers instead | — |
| **TCP(S-5a/b)** divided, on right or median shoulder | **The sheet contradicts itself** | Unresolved — see below |

One escape from the drawn shadow vehicle exists, and it is not automatic: S-2 Note 11 / S-3 Note 3 allow Type III barricades or other channelizing devices to be substituted **"when approved by the engineer."**

**TCP(S-5)-08 is internally inconsistent, and this repo does not resolve it.** Its plan callout reads "Work Vehicle," and the truck drawn carries none of the legend's black TMA chevron — but its own Notes 2 and 3 are written about "*the* Shadow Vehicle with TMA," wording carried over verbatim from S-3, where a shadow vehicle *is* drawn. Either the drawing shows the short-duration case, or the notes were copied and never reconciled. **The sheet does not say which.** Put the question to the Engineer rather than pick a reading.

**The surveying-specific catch, which duration does not reach.** TCP(S-1)-08A **Note 3**: if line-of-sight requirements for the surveying operation preclude placing the work vehicle where it protects workers, "the channelizing devices mentioned in Note 2 are required." Note 2 is the note that lets those devices be omitted under an hour — so Note 3 withdraws that relief, and the devices stand whatever the duration. *That last clause is a reading of the two notes together, not a phrase printed on the sheet.* A survey crew is in that case routinely, because sighting down a line is the job. TxDOT wrote this rule about surveyors specifically.

**No posted speed triggers anything, anywhere in the family. Not found on any of the six sheets** — 55 mph is an ordinary row in the taper, device-spacing and buffer tables on every one of them. The family's one speed break is S-1's advance signing: **3X at 50 mph or less, 1500 ft above 50 mph.** Longer signing, not a different crew.

**Freeway and controlled-access work is not found here.** All six sheets are footnoted **"Conventional Roads Only,"** and none uses the words *freeway* or *controlled access*. Divided conventional highways *are* covered — S-4 and S-5 are about nothing else. Look elsewhere before concluding TxDOT is silent on freeways.

!!! danger "Corrected 2026-09-13, under [issue #70](https://github.com/RickSmith/survey-recon/issues/70) — twice"

    **What this section used to say.** Until 2026-09-13 it read across from the
    mobile-operations standard **TCP(3-1)**, honestly labeled as such, because
    the surveying sheets could not be fetched at the time:

    > mobile TCPs apply on conventional roads ≤45 mph for work stopping up to
    > ~15 minutes. Beyond either threshold, a **stationary** TCP is required.
    >
    > **A 20-minute shot on a 55-mph highway converts a two-person crew into a
    > crew plus shadow truck.**

    **Half right — and right about the half that costs money.** Duration really
    can put a shadow truck on the job, on S-2b and S-3, where the sheet draws
    one. Somebody's instinct about a cost cliff was sound.

    **Wrong on every number and on the mechanism.** The line is **one hour**,
    not 15 or 20 minutes. It is not a speed threshold at all. And what happens
    at the line is that a *permission lapses*, leaving the drawn configuration
    standing, subject to the Engineer's discretion to accept barricades — which
    is not the same as a rule that adds a truck, and does not happen on S-1,
    S-2a, S-2c or S-4 at all.

    Nobody made the numbers up. **All three are real. Each governs something
    else.**

    | Number | Where it really comes from | What it actually governs |
    |---|---|---|
    | **~15 minutes** | TCP(S-2c)-10, MOBILE definition | The boundary between *mobile* and *short duration* work. A **classification**, with no requirement attached to crossing it |
    | **20 minutes** | TCP(S-2)-08A Note 7 | "Road closures shall be less than 20 minutes." A cap on how long a road may be **closed** with flaggers. Nothing to do with shadow trucks |
    | **45 mph** | TCP(S-3)-08 Note 7 | One CW20-5L "LEFT LANE CLOSED" sign per direction may be omitted below 45 mph **and** under 2000 ADT. It governs **one sign** |

    Three true facts from three different sheets, welded into a fourth claim
    that none of them makes. Not fabrication — **synthesis across sources that
    each looked authoritative.** Every number survives spot-checking. The
    sentence built from them does not.

    **The first correction was also wrong**, and that is the better lesson. It
    said flatly that no sheet in the family requires a shadow truck, read
    entirely out of the general notes — whose verbs are all soft: *desirable*,
    *may be replaced by*, *may be substituted*. Two reviewers checked the
    quotations and passed them, because the quotations were accurate.

    On a CAD standard sheet **the drawing states the requirement and the notes
    are exceptions to it.** Identical note wording means opposite things
    depending on what is drawn. The sheets had to be rendered and looked at
    before the TMA chevron — a separate legend symbol, on some trucks and not
    others — was visible at all. Text extraction flattens the legend, the notes
    and the plan view into one stream and destroys exactly the distinction that
    decides the cost. Recorded in
    [#71](https://github.com/RickSmith/survey-recon/pull/71).

**No TxDOT permit specific to surveyors working in state ROW was found** — RULIS covers utility installation and leasing. Stated as "not found," not "does not exist."

---

## Unverified — do not assert
1. ~~**TCP(S-1)-08A contents** — host blocked~~ **Resolved 2026-09-13.** All six TCP(S-\*) sheets are pulled and committed in [`project-sh16/manual-pulls/`](https://github.com/RickSmith/survey-recon/tree/main/project-sh16/manual-pulls). Two things about them stay unverified and are **"not found," not "does not exist"**: which protective vehicle **TCP(S-5)-08** requires — its drawing and its notes disagree, and the sheet does not say which governs — and what covers **freeway or controlled-access** survey work, since all six sheets are footnoted "Conventional Roads Only"
2. **Any published TxDOT ROE turnaround** — none found in the manuals
3. **THC Atlas ArcGIS layer inventory** — server exists, robots-blocked
4. **NOAA NCEI 1991–2020 normals dataset name** — docs only exemplify `daily-summaries`
5. **`landsurv.pdf`** "Request for Right Of Entry for Land Surveying" — appears in search, host blocks fetch

## Soundbites
- **"Oral right-of-entry is good for one day and one person."** — TxDOT's own manual
- **TxDOT ships a *second* request letter.** Non-response is the baseline.
- **§1071.3585 says a surveyor *may seek* a court order; §1071.358 says an LSLS *is entitled to* one.** Two words apart in the statute book, worlds apart in practice.
- **"There is no acceptable failure rate for any TxDOT survey."**
- **The agent confidently cited a superseded manual revision** because search results still point at the dead URL.
- **A survey crew on the centerline for more than an hour is looking at two shadow trucks.** TCP(S-3b) draws both of them. Under the hour, the crew's own truck will do.
- **TxDOT wrote a rule about sighting down a line.** TCP(S-1)-08A Note 3 — if line of sight will not let the work vehicle sit where it protects the crew, the channelizing devices are required however short the job.
- **Three true numbers, welded into a claim none of them makes.** 15 minutes, 20 minutes and 45 mph are each real and each governs something else. Every number survived spot-checking. The sentence built from them did not.
- **The notes said "desirable." The drawing said otherwise.** On a CAD standard sheet the drawing states the requirement and the notes are exceptions to it. An agent that reads text but cannot see a picture gets it backwards, and sounds confident doing it.

## Key source URLs
- Surveyors' Toolkit — https://www.txdot.gov/business/resources/surveyor-toolkit.html
- Survey Manual (ESS) — https://www.txdot.gov/manuals/row/ess/index.html
- ROW Preliminary Procedures Ch. 4 — https://www.txdot.gov/manuals/row/ppr/surveying_maps_and_parcels.html
- Monument specifications — https://www.txdot.gov/content/dam/docs/division/row/survey/monument-specifications.pdf
- Survey control SOP — https://www.txdot.gov/content/dam/docs/division/row/survey/survey-control.pdf
- GNSS accuracy levels — https://www.txdot.gov/content/dam/docs/division/row/survey/tsla.pdf
- ArcGIS submission standards — https://ftp.dot.state.tx.us/pub/txdot-info/row/arcgis/submission-standards.pdf
- Toolkit FTP mirror — https://ftp.dot.state.tx.us/pub/txdot/row/surveyor-toolkit/
- NGS Data Explorer API — https://geodesy.noaa.gov/web_services/data-explorer.shtml
- NGS Web Services index — https://geodesy.noaa.gov/web_services/
- TxDOT Open Data Portal — https://gis-txdot.opendata.arcgis.com/
- TMUTCD — https://www.txdot.gov/business/resources/traffic-design-standards/tmutcd.html
- Texas 811 — https://texas811.org/law/
- THC cemetery laws — https://thc.texas.gov/preserve/preservation-programs/cemetery-preservation/cemetery-laws
