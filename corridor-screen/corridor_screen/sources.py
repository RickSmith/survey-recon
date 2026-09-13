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
# Specification section 6 and `docs/txdot-research.md` both name
# `NPMS_Pipelines_2022` on `services.arcgis.com/G4S1dGvn7PIgYd6Y` as the
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
# This follows the service rather than the document, says so here, and the
# difference is raised on the pull request for the same ruling.

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
        "Lines. The Railroad Commission of Texas, not NPMS -- the NPMS service "
        "the specification names holds Pennsylvania data only. See trap two above."
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
