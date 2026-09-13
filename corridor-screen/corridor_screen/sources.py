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
