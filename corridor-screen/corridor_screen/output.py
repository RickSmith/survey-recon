"""The one file a screening run produces.

JSON, because a person and a program can both read it. One fetch, many
renderings: the bid memo, the flagged parcel table and the crew-day build-up
are separate jobs that all read this file rather than going back to the
services themselves.

Every block the specification names is present, including the blocks this
first pass does not fill. A block that is missing looks like an oversight. A
block that is present and says ``not-screened`` says what happened.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .cache import long_path, write_text

SCHEMA_VERSION = "0.1.0"

# The two flag types no public source publishes. Named in every output so the
# gap is visible rather than silent. A tool that says "I cannot see this, you
# must" is more use than one that quietly returns a shorter list.
NOT_SCREENABLE = [
    {"type": "gated access", "reason": "no public source publishes gate locations or access restrictions"},
    {"type": "livestock", "reason": "no public source publishes livestock presence"},
]


def map_link(bbox):
    """A public web map centered on the corridor.

    One click confirms the real-world location against real imagery. There is
    no basemap inside anything this tool writes, because a basemap would mean
    a network dependency inside the artifact.
    """
    lon = (bbox[0] + bbox[2]) / 2
    lat = (bbox[1] + bbox[3]) / 2
    return f"https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=13/{lat:.6f}/{lon:.6f}"


def not_screened(reason):
    """A block the specification names that this pass does not fill."""
    return {"status": "not-screened", "detail": reason}


def service_entry(source, ping, status, records, record_count, warnings=(), used=None):
    """One line of the honesty block.

    This is what lets somebody else decide whether to trust the file. It says
    exactly what was asked, of what, whether it answered, when that answer was
    captured, and what was doubted about it.
    """
    return {
        "name": source.name,
        "url": source.layer_url if source.layer_id is not None else source.base_url,
        "layer_id": source.layer_id,
        "purpose": source.purpose,
        "ping": ping.get("ping"),
        "ping_ms": ping.get("ms"),
        "ping_detail": ping.get("detail", ""),
        "status": status,
        "attempts": sum(r.get("attempts", 0) for r in records),
        "record_count": record_count,
        # When the answer was captured. A run replayed from the cache says how
        # old its data is; a reader who cannot see that cannot judge the file.
        "captured_at": next((r.get("captured_at") for r in records if r.get("captured_at")), None),
        "cache_files": [r["cache_key"] for r in records],
        "warnings": list(warnings),
        # How many of the records that came back were actually used. Any
        # service asked about a box gets one, because the box is wider than the
        # ribbon -- so "39 returned, 3 used" is a normal and honest pair of
        # numbers. Hiding the first would make the second look like the whole
        # answer.
        #
        # Until 2026-09-13, specification section 10 said "flag services
        # **only**". Control marks are asked about a box the same way and have
        # the same gap between returned and used, so the same pair is reported
        # for them. Raised on PR #54 rather than patched over, and Rick ruled on
        # 2026-09-13 that the rule belongs to any service asked about a box.
        # Section 10 now says so.
        "records_used": used,
    }


def skipped_service(source, reason, ping=None):
    """A service the run never got to.

    The reason goes in `detail`, not in `warnings`. `warnings` is the list of
    sanity checks that tripped, and each entry there has a shape -- check,
    severity, detail, what to do. A sentence of prose in that list would be the
    one thing this block exists to prevent: something that looks like a
    recorded doubt but cannot be read like one.
    """
    ping = ping or {}
    return {
        "name": source.name,
        "url": source.layer_url if source.layer_id is not None else source.base_url,
        "layer_id": source.layer_id,
        "purpose": source.purpose,
        "ping": ping.get("ping"),
        "ping_ms": ping.get("ms"),
        "ping_detail": ping.get("detail", ""),
        "status": "skipped",
        "detail": reason,
        "attempts": 0,
        "record_count": None,
        "captured_at": None,
        "cache_files": [],
        "warnings": [],
        "records_used": None,
    }


def build(run_id, started_at, mode, half_width_ft, adjacent_distance_ft, sanity_margin_ft, tool_version,
          alignment, corridor, services, parcel_rows, warnings,
          status="complete", stopped_at_service=None, corridor_flags=(),
          screened_for=(), lead_time_table=None, control=None, row_maps=None):
    """Assemble the whole output file."""
    return {
        "schema_version": SCHEMA_VERSION,
        "run": {
            "run_id": run_id,
            "started_at": started_at.isoformat(timespec="seconds"),
            "finished_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "status": status,
            "stopped_at_service": stopped_at_service,
            "mode": mode,
            "tool_version": tool_version,
            "half_width_ft": half_width_ft,
            "adjacent_distance_ft": adjacent_distance_ft,
            "sanity_margin_ft": sanity_margin_ft,
            "area": "texas-bexar",
            "not_screenable": NOT_SCREENABLE,
            "renderings": [],
            "map_link": map_link(corridor.bbox if corridor else alignment.bbox) if (corridor or alignment) else None,
            # The flag types this run actually checked for, run-wide. A type
            # that is not on this list was not looked for, and is never
            # reported as clear on any parcel.
            "screened_for": list(screened_for),
            "lead_times": lead_time_table or {},
        },
        "alignment": alignment.describe() if alignment else None,
        "corridor": corridor.describe() if corridor else None,
        "roadway": not_screened(
            "existing right-of-way width, lane count and traffic come from "
            "Roadway_Inventory_2023, which this pass does not call"
        ),
        "services": services,
        # NGS marks and their condition, from ``control.block``. A run that
        # never reached the service still gets a block, saying so -- built by
        # the same function, so a reader never has to work out which shape of
        # answer this is.
        "control": control if control is not None else not_screened(
            "the run did not reach the control step"
        ),
        # The ROW map sheets over the corridor, from ``row_maps.block``. A run
        # that never reached the service still gets a block, saying so -- built
        # by the same function, so a reader never has to work out which shape
        # of answer this is. Same rule as ``control`` above.
        "row_maps": row_maps if row_maps is not None else not_screened(
            "the run did not reach the ROW map step"
        ),
        "parcels": parcel_rows,
        # Things that cost time but belong to no single parcel -- a pipeline in
        # a road right of way no appraisal district taxes, a railway crossing
        # the route. Recorded against the run so nothing is quietly dropped for
        # being hard to attach.
        "corridor_flags": list(corridor_flags),
        "warnings": warnings,
    }


COMPLETE_NAME = "screening.json"
INCOMPLETE_NAME = "screening.incomplete.json"


def write(document, out_dir, name=None):
    """Write the output file.

    A run that stopped writes to its own file rather than over the last good
    one. The specification asks that a stopped run still produces an output,
    and it does -- but a demo rig whose whole point is repeatability must not
    let a blocked host on the morning of a session destroy a capture that
    already worked. The incomplete file sits beside the complete one and says
    which it is in its name.
    """
    if name is None:
        name = COMPLETE_NAME if document["run"]["status"] == "complete" else INCOMPLETE_NAME
    path = Path(out_dir) / name
    os.makedirs(long_path(path.parent), exist_ok=True)
    # ensure_ascii=False so a statutory citation reads as "Tex. Health & Safety
    # Code § 711.041" rather than "Tex. Health & Safety Code § 711.041".
    # Both are valid JSON and a program cannot tell them apart, but a person
    # reading this file on a projector can, and this file is meant to be read.
    # The file is written UTF-8 either way; see cache.write_text.
    write_text(path, json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    return path
