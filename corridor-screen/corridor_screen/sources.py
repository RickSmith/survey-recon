"""Every service this tool calls, named once, in one place.

The specification asks for exactly this: the Bexar field names in one named
block rather than scattered through the code, so that pointing the tool at
another county later is an edit and not a rewrite.

Layer numbers are load-bearing. Control is layer 67 and TxDOT-owned land is
layer 328. A tool that assumes layer 0 does not error -- it returns the wrong
data, quietly. ``checks.confirm_fields`` reads each layer before any query is
sent and refuses to run if the field list is not what is written here.

----

A correction, recorded rather than quietly fixed
================================================

Both ``docs/corridor-screen/spec.md`` section 10 and ``docs/txdot-research.md``
list the parcel fields as ``AcctNumb``, ``Owner``, ``LglDesc``, ``LglAcres``
and ``PropUse``. Those field names are real, but they belong to the **Bexar
County** parcel service at ``maps.bexar.org``, not to the CoSA BCAD service
the specification tells us to prefer.

Both services were read on 2026-09-12 and the two field lists were compared.
The CoSA service publishes ``Geo_id``, ``PropID``, ``Owner_Name``,
``legal_desc``, ``legal_acre`` and ``state_cd``. The research note appears to
have carried one service's field list across to the other.

This code follows the service, not the document, and the mapping below records
which name went where.

Amending a settled spec is not the agent's call, so the difference was raised on
[PR #52](https://github.com/RickSmith/survey-recon/pull/52) rather than patched
over. Rick ruled on 2026-09-13 that section 10 should carry the real field
names, and it now does, with a note recording the amendment. The account of how
the two lists came to be swapped stays in ``docs/txdot-research.md``.
"""


class Source:
    """One service, one layer, and what it is asked for."""

    def __init__(self, name, base_url, layer_id, purpose, required_fields=(), note=""):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.layer_id = layer_id
        self.purpose = purpose
        self.required_fields = tuple(required_fields)
        self.note = note

    @property
    def layer_url(self):
        return f"{self.base_url}/{self.layer_id}"

    @property
    def query_url(self):
        return f"{self.layer_url}/query"


TXDOT_AGOL = "https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services"
COSA_AGOL = "https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services"

ROADWAYS = Source(
    name="TxDOT_Roadways",
    base_url=f"{TXDOT_AGOL}/TxDOT_Roadways/FeatureServer",
    layer_id=0,
    purpose="alignment",
    required_fields=("RTE_NM", "BEGIN_DFO", "END_DFO"),
    note="Linear referencing. The geometry carries M values, which are DFO.",
)

PARCELS = Source(
    name="BCAD_Parcels",
    base_url=f"{COSA_AGOL}/BCAD_Parcels/FeatureServer",
    layer_id=0,
    purpose="parcels",
    required_fields=("Geo_id", "PropID", "Situs", "Owner_Name", "legal_desc", "legal_acre", "state_cd"),
    note="CoSA's copy of the Bexar Appraisal District parcels. Refreshed weekly.",
)

GEOMETRY = Source(
    name="ArcGIS_Geometry",
    base_url="https://utility.arcgisonline.com/arcgis/rest/services/Geometry/GeometryServer",
    layer_id=None,
    purpose="buffer",
    required_fields=(),
    note="Builds the corridor polygon, so no geometry library has to be installed.",
)

# How a parcel row is built from what the CoSA service publishes. Left side is
# the field name in this tool's output; right side is the field name on the
# service. Pointing this tool at another county starts here.
BEXAR_PARCEL_FIELDS = {
    # Geo_id is the appraisal district's own geographic identifier and is what a
    # parcel should be quoted by. Some records publish no Geo_id -- road slivers
    # and similar -- so PropID is tried next, and a parcel with neither gets an
    # identifier made from its shape. Every row says in `id_source` which of the
    # three it got, because only the first two can be quoted back to Bexar County.
    "id": "Geo_id",
    "id_fallback": "PropID",
    "owner": "Owner_Name",
    "situs": "Situs",
    "legal_description": "legal_desc",
    "legal_acres": "legal_acre",
    # The appraisal district publishes the Texas state property-use code here,
    # not a plain-English description. Reported as the code it is.
    "property_use": "state_cd",
}


# -- The flag services ------------------------------------------------------
#
# Four flag types, from issue #17: schools, cemeteries, railroads and
# pipelines. Each one is a public map service, each one was queried live on
# 2026-09-12, and two of the four had a trap in them worth recording here.
#
# ----
#
# Trap one: field names come back in a different case than they are published
# ==========================================================================
#
# The USGS `structures` layers publish their fields as `NAME`,
# `PERMANENT_IDENTIFIER` and so on, in capitals -- and answer a query with
# `name` and `permanent_identifier`, in lower case. The USGS `transportation`
# layers publish them in lower case and answer in lower case.
#
# So a field list check that compares capitals against capitals passes, and the
# code that then reads `feature["attributes"]["NAME"]` finds nothing and
# silently reports every school as unnamed. Reading attributes case-insensitively
# is why `flags.attribute` exists rather than a plain dictionary lookup.
#
# ----
#
# Trap two: the pipeline service in the specification holds no Texas data
# ======================================================================
#
# NPMS is the National Pipeline Mapping System, run by the federal Pipeline and
# Hazardous Materials Safety Administration. TPMS is the Texas Pipeline Mapping
# System, run by the Railroad Commission of Texas. Two different bodies, two
# different datasets, and only one of them covers Texas.
#
# Until 2026-09-13, specification section 6 and `docs/txdot-research.md` both
# named `NPMS_Pipelines_2022` on `services.arcgis.com/G4S1dGvn7PIgYd6Y` as the
# pipeline source. Read on 2026-09-12, that service holds **543 records, all of
# them in Chester County, Pennsylvania**. Its own extent is around longitude
# -76, latitude 40. A query for Texas returns zero records and no error.
#
# That is the same trap this repo's own research already records for
# `FEMA_Flood_Zones` on services9, which "ranks high in search but is Salem, MA
# only." The research fell into its own documented trap a second time, and the
# only reason it was caught is that a corridor with zero pipelines looked wrong
# enough to check the county, and then the state.
#
# The source used instead is the **Texas Pipeline Mapping System (TPMS)**,
# published by the Railroad Commission of Texas, which is the Texas authority
# for pipeline location. It holds 490,375 records, 598 of them within a box
# around Bexar County. Read on 2026-09-12.
#
# Amending a settled spec is not the agent's call -- the precedent is the
# `AcctNumb` correction above, which was raised on PR #52 and ruled on by Rick.
# This followed the service rather than the document and raised the difference
# on PR #53: https://github.com/RickSmith/survey-recon/pull/53
#
# Rick ruled on 2026-09-13 that section 6 should name the source that holds
# Texas data. It now names TPMS, with a note recording the amendment, so this
# code and the specification agree again.

USGS_CARTO = "https://carto.nationalmap.gov/arcgis/rest/services"
RRC_PUBLIC = "https://gis.rrc.texas.gov/server/rest/services/rrc_public"

SCHOOLS = Source(
    name="USGS_Structures_Schools",
    base_url=f"{USGS_CARTO}/structures/MapServer",
    layer_id=23,
    purpose="flag:school",
    required_fields=("PERMANENT_IDENTIFIER", "NAME", "FTYPE", "FCODE"),
    note="Points. Published in capitals, answered in lower case -- see trap one above.",
)

CEMETERIES = Source(
    name="USGS_Structures_Cemeteries",
    base_url=f"{USGS_CARTO}/structures/MapServer",
    layer_id=2,
    purpose="flag:cemetery",
    required_fields=("PERMANENT_IDENTIFIER", "NAME", "FTYPE", "FCODE"),
    note="Points. Same server and same casing trap as the schools layer.",
)

RAILROADS = Source(
    name="USGS_Transportation_Railroads",
    base_url=f"{USGS_CARTO}/transportation/MapServer",
    layer_id=38,
    purpose="flag:railroad",
    required_fields=("permanent_identifier", "name", "railowner"),
    note="Lines. This layer publishes lower case, unlike structures on the same host.",
)

PIPELINES = Source(
    name="RRC_TPMS_Pipelines",
    base_url=f"{RRC_PUBLIC}/tpms/MapServer",
    layer_id=0,
    purpose="flag:pipeline",
    required_fields=("TPMS_ID", "OPER_NM", "CMDTY_DESC", "STATUS_CD"),
    note=(
        "Lines. The Texas Pipeline Mapping System, from the Railroad Commission of "
        "Texas -- not the National Pipeline Mapping System service the "
        "specification names, which holds Pennsylvania data only. See trap two."
    ),
)

# One flag type per source, and the key into the lead-time table. Keeping the
# three together means a new flag type is one entry here, a row in
# lead_times.toml, and nothing else.
FLAG_SOURCES = (
    (SCHOOLS, "school"),
    (CEMETERIES, "cemetery"),
    (RAILROADS, "railroad"),
    (PIPELINES, "pipeline"),
)

# Which attribute holds the feature's own name, and which holds its identifier,
# per service. Read case-insensitively, so the casing trap above cannot bite.
FLAG_FIELDS = {
    SCHOOLS.name: {"name": "NAME", "id": "PERMANENT_IDENTIFIER"},
    CEMETERIES.name: {"name": "NAME", "id": "PERMANENT_IDENTIFIER"},
    RAILROADS.name: {"name": "name", "id": "permanent_identifier", "operator": "railowner"},
    PIPELINES.name: {"name": "CMDTY_DESC", "id": "TPMS_ID", "operator": "OPER_NM"},
}


# -- Control ----------------------------------------------------------------
#
# NGS survey marks, from issue #17's sibling, issue #14. Recovery against
# setting new is what drives an estimate, so what these records are pulled for
# is one field: the condition the mark was last left in.
#
# ----
#
# Two services publish the same marks, and only one of them takes a corridor
# ================================================================================
#
# Specification section 6 names both: "NGS Data Explorer `/radial`, and the NGS
# datasheets feature service."
#
# The Data Explorer API at `geodesy.noaa.gov/api/nde/` takes a point and a
# radius, or a north-south-east-west box. It does not take a corridor, it caps
# at 500 records, and it is not an ArcGIS service, so none of the paging, field
# list checking or provenance machinery in this tool would reach it.
#
# The datasheets feature service is a plain ArcGIS feature service. It takes
# arbitrary geometry, pages at 2,000, and answers the same questions every
# other source here answers. So the feature service is what this tool calls.
#
# The API was still worth the call once, as a cross-check -- see below.
#
# ----
#
# The condition field is called something else on the service
# ==========================================================
#
# Specification section 11 says `condition` is carried through and never
# dropped, and issue #14 names `MARK NOT FOUND` as the value that matters. The
# Data Explorer API does publish a field called `condition`. **The feature
# service does not.** It publishes `LAST_COND`, which the research note already
# warned about in one line: "Field names differ from the NDE API."
#
# A tool that reads `condition` off this service finds nothing, raises nothing,
# and reports every mark in the corridor as having no known condition. On SH16
# the eleven marks nobody could find would read as eleven unknowns -- and an
# unknown reads to an estimator as "go and look," which is the trip this field
# exists to prevent.
#
# That the two are the same field was confirmed rather than assumed. Both
# services were asked about PIDs `AY0713`, `AY0710` and `AY1102` on 2026-09-12,
# and answered the same condition and the same recovery date for all three. The
# API calls it `condition`; the feature service calls it `LAST_COND`. The answer
# is cached like any other, at
# `ngs-data-explorer/pid-cross-check-ay0713-ay0710-ay1102`, so the claim can be
# checked rather than taken. The mapping below records which name went where,
# the same way `BEXAR_PARCEL_FIELDS` does.
#
# This is a field mapping, not a correction to the specification. Section 11
# describes the output file, and the output file does carry `condition`.

NGS_AGOL = "https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services"

NGS_MARKS = Source(
    name="NGS_Datasheets",
    base_url=f"{NGS_AGOL}/NGS_Datasheets_Feature_Service/FeatureServer",
    layer_id=1,
    purpose="control:ngs",
    required_fields=(
        "PID",
        "NAME",
        "STAMPING",
        "MARKER",
        "SETTING",
        "STABILITY",
        "LAST_COND",
        "LAST_RECV",
        "LAST_RECBY",
        "POS_DATUM",
        "VERT_DATUM",
        "ORTHO_HT",
        "SPC_ZONE",
        "POS_ORDER",
        "VERT_ORDER",
        "CORS_ID",
        "PACS_SACS",
    ),
    note=(
        "Points, one per mark. Layer 1 is the only layer on this service and is "
        "named ALL_DATASHEETS. The condition field is LAST_COND, not condition."
    ),
)

# How an NGS mark row is built from what the datasheets service publishes. Left
# side is the field name in this tool's output; right side is the field name on
# the service. Same shape and same job as `BEXAR_PARCEL_FIELDS` above.
NGS_MARK_FIELDS = {
    "pid": "PID",
    # The whole reason to pull the marks. See the note above on why it is not
    # spelled `condition` here.
    "condition": "LAST_COND",
    "last_recovered": "LAST_RECV",
    "last_recovered_by": "LAST_RECBY",
    # NGS calls this the mark's designation. `NAME` on this service.
    "designation": "NAME",
    "stamping": "STAMPING",
    # What kind of monument it is, and what it is set in. Both come back as a
    # code and its meaning in one string, for example
    # "DB = BENCH MARK DISK" -- reported as the service writes it.
    "marker": "MARKER",
    "setting": "SETTING",
    "stability": "STABILITY",
    "horizontal_datum": "POS_DATUM",
    "vertical_datum": "VERT_DATUM",
    # Meters, and NGS publishes it as a string. Reported as it came.
    "ortho_height": "ORTHO_HT",
    "spc_zone": "SPC_ZONE",
    "horizontal_order": "POS_ORDER",
    "vertical_order": "VERT_ORDER",
    # Set where the mark is a CORS, or part of a PACS/SACS pair.
    "cors_id": "CORS_ID",
    "pacs_sacs": "PACS_SACS",
}


# -- ROW map sheets ---------------------------------------------------------
#
# The historical record drawings, from issue #16. Old sheets mean hand
# retracement off a scan, and that is time on the estimate -- so the two
# numbers wanted here are how many sheets and how far back they go.
#
# Three things about this service are unlike every other one in this file.
#
# ----
#
# It is a MapServer, and it is the host the spec calls least reliable
# ===================================================================
#
# Every other service here is a FeatureServer on a cloud host. This one is a
# MapServer on TxDOT's own `maps.dot.state.tx.us`, which specification section
# 5 names "the least reliable host, deliberately last," and which this repo's
# own research recorded failing and then succeeding minutes later.
#
# The URL shape is the same -- `<base>/<layer>/query` -- so `Source` reaches it
# unchanged, and the reachability ping is doing real work on this one.
#
# ----
#
# Its dates are real date fields, and two thirds of them are negative
# ===================================================================
#
# `MAP_FROM_DT` and `MAP_TO_DT` are `esriFieldTypeDate`, which ArcGIS sends as
# milliseconds since 1970. Every sheet older than 1970 is a negative number,
# and on Windows the obvious way to read one raises `OSError` rather than
# returning a wrong date. The whole account, and the arithmetic that works, is
# at the top of `row_maps.py`.
#
# ----
#
# `ROW_MAP_ID` looks like a key and is not
# ========================================
#
# Six of the 27 SH16 sheets in Bexar County share `ROW_MAP_ID` 993. `MAP_NM`
# is the one-per-drawing name. Counting distinct identifiers gives 22 rather
# than 27, and that is the kind of wrong number that looks right.
#
# Read live on 2026-09-12. Written up in
# `docs/data-sources/row-map-sheets.md`.

TXDOT_MAPS = "https://maps.dot.state.tx.us/arcgis/rest/services"

ROW_MAPS = Source(
    name="TxDOT_ROW_Maps",
    base_url=f"{TXDOT_MAPS}/ROW/ROW_Maps_CL_2017/MapServer",
    layer_id=0,
    purpose="row-maps",
    required_fields=(
        "MAP_NM",
        "ROW_MAP_ID",
        "CTRL_SECT_NBR",
        "CSJ_NBR",
        "RTE_NM",
        "CNTY_NM",
        "MAP_FROM_DT",
        "MAP_TO_DT",
        "TOTL_MAP_PAGE_QTY",
        "MAP_LMT_FROM_DSCR",
        "MAP_LMT_TO_DSCR",
    ),
    note=(
        "Lines, one per drawing. A MapServer rather than a FeatureServer, and the "
        "layer name is RPAM.RPAM.VW_ROW_MAP_HyLink. Paging cap 5,000. The dates "
        "are real date fields -- milliseconds, negative before 1970."
    ),
)

# How a ROW map sheet row is built from what the service publishes. Left side
# is the field name in this tool's output; right side is the field name on the
# service. Same shape and same job as `BEXAR_PARCEL_FIELDS` and
# `NGS_MARK_FIELDS` above.
ROW_MAP_FIELDS = {
    # One per drawing. TxDOT builds it as District-ControlSection-Route-Date,
    # for example SAT-029110-SH0016-19980306, with a `-1` suffix when two
    # sheets carry the same date. It states the sheet's date a second time,
    # which is what makes the date reading checkable.
    "map_name": "MAP_NM",
    # Carried through as what it is. Not a unique key -- see the note above.
    "row_map_id": "ROW_MAP_ID",
    "control_section": "CTRL_SECT_NBR",
    "csj": "CSJ_NBR",
    "route": "RTE_NM",
    "county": "CNTY_NM",
    # The field the ticket exists for. See the date trap above.
    "map_from_date": "MAP_FROM_DT",
    "map_to_date": "MAP_TO_DT",
    "total_pages": "TOTL_MAP_PAGE_QTY",
    # What the sheet says its own limits are, in TxDOT's words.
    "limit_from": "MAP_LMT_FROM_DSCR",
    "limit_to": "MAP_LMT_TO_DSCR",
}


# -- TxDOT primary control points -------------------------------------------
#
# Issue #15. TxDOT's own control, beside the NGS marks above. A corridor with
# TxDOT primary control already set in it is a corridor where a crew ties into
# something that exists; a corridor without it is one where control gets set.
#
# ----
#
# The layer is 67, and the reason to write that down is not the reason expected
# ============================================================================
#
# Specification section 6, `docs/txdot-research.md` and issue #15 all say the
# same thing: control is layer 67, not layer 0, and "a tool that assumes layer 0
# does not error -- it returns the wrong data, quietly."
#
# **On this service, that second half is not true, and it was checked.** Asked
# for layer 0 on 2026-09-12, `Primary_Control_Points/FeatureServer` answers:
#
#     HTTP 400 -- The requested layer (layerId: 0) was not found.
#
# Layer 67 is the only layer on the service. `2025_Land_Parcels` answers the
# same way about its layer 0, and layer 328 is the only layer there. So on both
# of the services this repo keeps naming, a hardcoded layer 0 fails loudly.
#
# The trap is real all the same, and it is one step further out. The thing that
# answers quietly is not the wrong *layer*, it is the wrong *service*:
#
#     TxDOT_Control_Sections/FeatureServer/0
#
# That exists, it is layer 0, it answers a corridor query without erroring, and
# it holds **control sections** -- the numbered highway segments in
# `CONTEXT.md`, e.g. SH16's 0291-09 -- which are not survey control and are not
# monuments. An agent told to find "TxDOT control" and reaching for layer 0
# lands there and gets a plausible answer to the wrong question.
#
# The guard is the same either way and it runs before any query is sent:
# `checks.confirm_fields` reads the layer's published field list and refuses to
# go on unless the fields below are on it. Control sections publish `RTE_NM` and
# `CTRL_SECT_NBR` and nothing resembling `MONUMENT_COND_DSCR`, so the check
# stops that run on its first request.
#
# The difference between what issue #15 says and what the service does is
# recorded rather than quietly fixed, the same as `AcctNumb` on PR #52 and
# `NPMS` on PR #53. Raised on issue #15, and Rick ruled on 2026-09-13 that
# specification section 6 should say what the services actually do. It now
# does, with a note recording the amendment, so this code and the
# specification agree again.
#
# ----
#
# This is the San Antonio district's control, not the state's
# ===========================================================
#
# The service's published title is **"San Antonio District Primary Control
# Points"**,
# and `docs/txdot-research.md` records "766 statewide." Both numbers are right
# and together they mislead. Read on 2026-09-12, all 766 records are there, and
# **715 of them are in district 15, San Antonio**. The rest are a handful spilled
# into neighboring districts: 14 (22 records), 13 (14), 16 (9), 22 (4), 7 (2).
#
# For SH16 in Bexar that is the right dataset and a complete one -- 376 records
# in Bexar County alone. Pointed at a corridor in Lubbock or Tyler it returns
# nothing, and nothing would read as "TxDOT has set no control here."
#
# That is `unknown` reported as `no`, which `CONTEXT.md` is bluntest about. The
# tool's `area` is `texas-bexar`, so the limit does not bite today. It is
# written here, and on the data-sources page, so that whoever points this at
# another county reads it before the count does the damage.
#
# ----
#
# `N/A` is this service's blank, and it is a non-empty string
# ==========================================================
#
# The NGS service writes a single space where it has nothing. This one writes
# the three characters `N/A`: on 649 of 766 `NGS_PERM_ID` values, 24 conditions,
# 10 stability codes, and nearly every `GEOID_NM` and `PROJ_NBR`.
#
# `arcgis.attribute` strips whitespace, so the NGS blank falls away on its own.
# `N/A` survives it. A condition of `N/A` read as a value becomes "condition
# reported," and a monument nobody has assessed goes into an estimate as control
# you have. `control.published` is what turns it back into nothing.

TXDOT_CONTROL = Source(
    name="TxDOT_Primary_Control_Points",
    base_url=f"{TXDOT_AGOL}/Primary_Control_Points/FeatureServer",
    # Not 0. See the long note above -- and note that the reason to write it
    # down turned out not to be the reason the ticket gave.
    layer_id=67,
    purpose="control:txdot",
    required_fields=(
        "OBJECTID",
        "STATN_NM",
        "MONUMENT_COND_DSCR",
        "MONUMENT_STAMPING_TXT",
        "MONUMENT_STBL_CD",
        "MONUMENT_LOGO_TYPE_NM",
        "MRKR_DSCR",
        "NGS_PERM_ID",
        "LAST_RCOV_DT",
        "INTERVSBL_STATN_NM",
        "INTERVSBL_DSTNCE_MS",
        "TXDOT_QLTY_LEVEL_CD",
        "HRZNTL_DATUM_NM",
        "VERT_DATUM_NM",
        "STATE_PLN_ZN_NM",
        "GEOID_NM",
        "STATN_LAT",
        "STATN_LON",
        "STATN_EL",
        "STATN_NORTHING_MS",
        "STATN_EASTING_MS",
        "STATN_GRID_SCL_FCTR_MS",
        "STATN_EL_FCTR_MS",
        "STATN_COMBN_SCL_FCTR_MS",
        "UOM_NM",
        "STATN_LOCN_DSCR",
        "RTE_NM",
        "CNTY_NM",
        "TXDOT_DIST_NBR",
        "PDF_Filename",
    ),
    note=(
        "Points, one per monument. Layer 67 is the only layer on this service. "
        "Its own coordinates are WKID 103161, so every query passes outSR=4326 "
        "-- which _extent_query already does for every service here."
    ),
)

# How a TxDOT control point row is built from what layer 67 publishes. Left side
# is the field name in this tool's output; right side is the field name on the
# service. Same shape and same job as `NGS_MARK_FIELDS` above.
TXDOT_CONTROL_FIELDS = {
    # The monument's own name, and what a party chief will call it. This service
    # publishes no PID of its own; `STATN_NM` is the identifier.
    "station": "STATN_NM",
    # The field this whole block exists for, same as `LAST_COND` on NGS. Five
    # values on 2026-09-12: Good (706), N/A (24), Destroyed (18), Unknown (9),
    # Poor (9). Mixed case, where NGS answers in capitals.
    "condition": "MONUMENT_COND_DSCR",
    # Milliseconds since 1970, not the eight-digit string NGS publishes, and set
    # on only 14 of 766 records. See `control._epoch_date`.
    "last_recovered": "LAST_RCOV_DT",
    # Where a TxDOT monument and an NGS mark are the same monument. `N/A` on 649
    # of 766 records, which is the placeholder and not a PID.
    "ngs_pid": "NGS_PERM_ID",
    "stamping": "MONUMENT_STAMPING_TXT",
    "stability": "MONUMENT_STBL_CD",
    "monument_logo": "MONUMENT_LOGO_TYPE_NM",
    # What the monument physically is, e.g. "Aluminum Cap in Concrete".
    "marker": "MRKR_DSCR",
    # TxDOT's own control quality level code. `2` on 764 of 766 records and `3`
    # on the other two. Reported as the code it is.
    #
    # What the code maps to is **not found**. Survey Manual Ch. 3 gives primary
    # control as "Level 2A" and secondary as "Level 3"
    # (https://www.txdot.gov/manuals/row/ess/index.html), and this service
    # publishes a bare `2` with no `A`. Whether the two numbering schemes are the
    # same one is not something the service says, and the manual does not
    # mention this field. Looked for in the Survey Manual chapter list and in
    # the layer's own metadata, which carries no description or coded-value
    # domain. So the code travels through and nobody's estimate rests on a
    # mapping this tool guessed.
    "quality_level": "TXDOT_QLTY_LEVEL_CD",
    # TxDOT requires primary control in intervisible pairs, so the partner
    # station is data an estimator needs, not trivia. Set on 752 of 766.
    "intervisible_station": "INTERVSBL_STATN_NM",
    "intervisible_distance": "INTERVSBL_DSTNCE_MS",
    "horizontal_datum": "HRZNTL_DATUM_NM",
    "vertical_datum": "VERT_DATUM_NM",
    "spc_zone": "STATE_PLN_ZN_NM",
    "geoid": "GEOID_NM",
    # The service's own published position, beside the geometry it returns.
    # Carried so `checks.check_published_position` can compare the two.
    "published_latitude": "STATN_LAT",
    "published_longitude": "STATN_LON",
    # Grid coordinates and elevation, in whatever `UOM_NM` says -- US Survey
    # Feet on all 766 records read on 2026-09-12.
    "northing": "STATN_NORTHING_MS",
    "easting": "STATN_EASTING_MS",
    "elevation": "STATN_EL",
    "units": "UOM_NM",
    # TxDOT requires all control coordinates in surface and grid both, and these
    # are the numbers that convert between them. Reported, never applied.
    "grid_scale_factor": "STATN_GRID_SCL_FCTR_MS",
    "elevation_factor": "STATN_EL_FCTR_MS",
    "combined_scale_factor": "STATN_COMBN_SCL_FCTR_MS",
    # The to-reach description, in the same spirit as an NGS datasheet's.
    "to_reach": "STATN_LOCN_DSCR",
    "route": "RTE_NM",
    "county": "CNTY_NM",
    "district": "TXDOT_DIST_NBR",
    # The control sheet's filename, e.g. `SCP_32.pdf`. A bare filename with no
    # base address published anywhere -- see `control.attachment_url`.
    "pdf_filename": "PDF_Filename",
}


# -- The crew safety sheet --------------------------------------------------
#
# Issue #18. Where the nearest help is, for the crew standing on the road --
# not a bid question, and kept apart from the flags in the output for that
# reason. All four layers live on the same USGS structures server the school
# and cemetery flags already use, and they publish an identical field list.
#
# ----
#
# Every layer on this service exists twice, and the copies are identical
# =====================================================================
#
# `structures/MapServer` publishes two group layers -- `Labels` at 0 and
# `Features` at 35 -- and every feature layer appears once under each. Hospitals
# are layer 14 and also layer 49. Ambulance services are 15 and also 50. Fire
# and EMS are 16 and also 51. Police stations are 18 and also 53.
#
# Read live on 2026-09-13, both copies of all four answered the same box with
# the same count: 17 hospitals, 13 ambulance services, 31 fire or EMS stations,
# 13 police stations. Both are plain point feature layers with the same fields.
#
# So this is a trap that does not bite -- but only because it was checked. The
# lower set is used, which is what specification section 6 names and what the
# school and cemetery flags on this same server already use.
#
# ----
#
# Police was not in the specification, and the ticket asked for it
# ================================================================
#
# Until 2026-09-13, section 6 listed this server's layers as "Cemeteries,
# Historic, Hospitals, Ambulance, Fire and EMS, Schools -- 2, 11, 14, 15, 16,
# 23," with no police row at all. Issue #18 asks for "nearest hospital, nearest
# EMS, nearest police" in as many words, so `Police Stations`, layer 18, is
# called. Layer 17 is the `Law Enforcement` group above it and layer 19 is
# `Prisons/Correctional Facilities`, which is not what was asked for.
#
# Amending a settled spec is not the agent's call -- the precedent is `AcctNumb`
# on PR #52, `NPMS` on PR #53, the control blocks on PR #54 and the ROW map
# block on PR #56. This was raised on PR #57, and Rick ruled on 2026-09-13.
# Section 6 now carries police, and splits that row in two: the flags and the
# crew safety sheet are different steps, asked different questions about
# different extents. Section 5 gained step 9 and section 10 gained the
# `crew_safety` block on the same ruling, so this code and the specification
# agree again.
#
# ----
#
# EMS is two layers, not one
# ==========================
#
# USGS splits it. `Ambulance Services` is layer 15 and `Fire Stations/EMS
# Stations` is layer 16, and on this corridor they return different places --
# the nearest ambulance service is Alamo Area Ambulance and the nearest fire or
# EMS station is Helotes Fire Department. Asking only one of them would answer
# the ticket's "nearest EMS" with half the data, so both are asked and reported
# separately rather than merged.
#
# The casing trap at the top of this section applies to all four: published in
# capitals, answered in lower case. `arcgis.attribute` is what handles it.
#
# Written up in `docs/data-sources/crew-safety.md`.

# All four layers publish this identical list, so it is written once. The field
# list check reads it off each layer before any query is sent, which is what
# would catch the wrong one of the two copies quietly changing.
SAFETY_REQUIRED_FIELDS = (
    "PERMANENT_IDENTIFIER",
    "NAME",
    "ADDRESS",
    "CITY",
    "STATE",
    "ZIPCODE",
    "LOADDATE",
)

HOSPITALS = Source(
    name="USGS_Structures_Hospitals",
    base_url=f"{USGS_CARTO}/structures/MapServer",
    layer_id=14,
    purpose="safety:hospital",
    required_fields=SAFETY_REQUIRED_FIELDS,
    note="Points. Also published at layer 49 under the Features group -- same data.",
)

AMBULANCE = Source(
    name="USGS_Structures_Ambulance",
    base_url=f"{USGS_CARTO}/structures/MapServer",
    layer_id=15,
    purpose="safety:ambulance",
    required_fields=SAFETY_REQUIRED_FIELDS,
    note="Points. One of the two layers USGS splits EMS across. Also at layer 50.",
)

FIRE_EMS = Source(
    name="USGS_Structures_Fire_EMS",
    base_url=f"{USGS_CARTO}/structures/MapServer",
    layer_id=16,
    purpose="safety:fire_ems",
    required_fields=SAFETY_REQUIRED_FIELDS,
    note="Points. The other half of EMS. Also at layer 51.",
)

POLICE = Source(
    name="USGS_Structures_Police",
    base_url=f"{USGS_CARTO}/structures/MapServer",
    layer_id=18,
    purpose="safety:police",
    required_fields=SAFETY_REQUIRED_FIELDS,
    note=(
        "Points. Not named in specification section 6 -- issue #18 asks for it. "
        "Layer 17 is the Law Enforcement group above it. Also at layer 53."
    ),
)

# One safety type per source, in the order a party chief reads them. Keeping the
# pair together means a new type is one entry here and nothing else.
SAFETY_SOURCES = (
    (HOSPITALS, "hospital"),
    (AMBULANCE, "ambulance"),
    (FIRE_EMS, "fire_ems"),
    (POLICE, "police"),
)

# The types this tool knows about, named once. A type not on this list cannot be
# reported on at all, which is what stops a missing key reading as "none here".
SAFETY_TYPES = tuple(kind for _, kind in SAFETY_SOURCES)

# How a safety place is built from what the structures layers publish. Left side
# is the field name in this tool's output; right side is the field name on the
# service. Same shape and same job as `BEXAR_PARCEL_FIELDS`, `NGS_MARK_FIELDS`
# and `ROW_MAP_FIELDS` above. All four layers publish this identical list.
SAFETY_FIELDS = {
    "id": "PERMANENT_IDENTIFIER",
    "name": "NAME",
    # What a party chief needs beyond a name. A name with no address is a name
    # somebody has to look up on a phone that may have no signal.
    "address": "ADDRESS",
    "city": "CITY",
    "state": "STATE",
    "zipcode": "ZIPCODE",
    # A real date field, so milliseconds -- read through `arcgis.from_epoch_ms`,
    # the same function TxDOT's ROW map dates go through and for the same
    # reason. The day USGS loaded the record, never the day anybody confirmed
    # the place is still open.
    "load_date": "LOADDATE",
}
