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


def service_entry(source, ping, status, records, record_count, warnings=()):
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
    }


def build(run_id, started_at, mode, half_width_ft, adjacent_distance_ft, tool_version,
          alignment, corridor, services, parcel_rows, warnings,
          status="complete", stopped_at_service=None):
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
            "area": "texas-bexar",
            "not_screenable": NOT_SCREENABLE,
            "renderings": [],
            "map_link": map_link(corridor.bbox if corridor else alignment.bbox) if (corridor or alignment) else None,
        },
        "alignment": alignment.describe() if alignment else None,
        "corridor": corridor.describe() if corridor else None,
        "roadway": not_screened(
            "existing right-of-way width, lane count and traffic come from "
            "Roadway_Inventory_2023, which this pass does not call"
        ),
        "services": services,
        "control": not_screened(
            "NGS marks and TxDOT primary control points are separate work orders"
        ),
        "row_maps": not_screened(
            "the ROW map sheet index is a separate work order"
        ),
        "parcels": parcel_rows,
        "corridor_flags": [],
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
    write_text(path, json.dumps(document, indent=2) + "\n")
    return path
