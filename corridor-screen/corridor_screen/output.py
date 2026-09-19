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


# What a service entry says about where its answer came from. Specification
# section 10 names four values: `ok`, `failed`, `from-cache` and `skipped`.
FETCHED = "ok"
FROM_CACHE = "from-cache"


def status_of(records):
    """Where this service's answer came from, read off the responses themselves.

    Every response carries its own `status` -- `ok` when the network was asked,
    `from-cache` when it was not. A service answered entirely from disk says
    `from-cache`; one that had to ask says `ok`.

    **This used to be the literal string "ok", passed in by every one of the
    eight call sites.** The responses carried the truth and nothing read it, so
    the word `from-cache` appeared nowhere in any output file this tool had ever
    written -- and a run replayed from disk was, in its own honesty block,
    byte-identical to one that had just called fourteen services. That is the
    one field in the block whose job is to say where the answer came from.

    Found by the review on issue #19 and fixed there. A cache-first run that had
    to fetch part of a service reads `ok`, because it did ask; `attempts` and
    `captured_at` beside it carry how much and how old.
    """
    if not records:
        return FETCHED
    return FROM_CACHE if all(r.get("status") == FROM_CACHE for r in records) else FETCHED


def service_entry(source, ping, records, record_count, warnings=(), used=None):
    """One line of the honesty block.

    This is what lets somebody else decide whether to trust the file. It says
    exactly what was asked, of what, whether it answered, where the answer came
    from, when it was captured, and what was doubted about it.
    """
    return {
        "name": source.name,
        "url": source.layer_url if source.layer_id is not None else source.base_url,
        "layer_id": source.layer_id,
        "purpose": source.purpose,
        "ping": ping.get("ping"),
        "ping_ms": ping.get("ms"),
        "ping_detail": ping.get("detail", ""),
        "status": status_of(records),
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

    **A skipped service can still have left a file, and it is named here.** The
    ping saves whatever the host said, an error included -- see
    ``arcgis.Fetcher.ping``. Leaving ``cache_files`` empty would put the reason
    on screen and hide the evidence for it, which is the reverse of what this
    block is for, and on a blocked host nothing else in the run points at that
    record. A cache-only run makes no ping and so still lists nothing.
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
        "cache_files": [key for key in [ping.get("cache_key")] if key],
        "warnings": [],
        "records_used": None,
    }


def build(run_id, started_at, mode, half_width_ft, adjacent_distance_ft, sanity_margin_ft, tool_version,
          alignment, corridor, services, parcel_rows, warnings,
          status="complete", stopped_at_service=None, corridor_flags=(),
          screened_for=(), lead_time_table=None, control=None, row_maps=None,
          crew_safety=None, safety_search_miles=None, roadway=None):
    """Assemble the whole output file."""
    return {
        "schema_version": SCHEMA_VERSION,
        "run": {
            "run_id": run_id,
            "started_at": started_at.isoformat(timespec="seconds"),
            "finished_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            # The run's own status -- `complete` or `incomplete`. Not the same
            # word as a service's `status`, which says where its answer came
            # from. Two different questions that share a name.
            "status": status,
            "stopped_at_service": stopped_at_service,
            "mode": mode,
            "tool_version": tool_version,
            "half_width_ft": half_width_ft,
            "adjacent_distance_ft": adjacent_distance_ft,
            "sanity_margin_ft": sanity_margin_ft,
            # The fourth stated distance. It sits here with the other three
            # rather than only inside `crew_safety`, because every distance
            # this run was given is a number a person chose and the run block
            # is where they are read together.
            "safety_search_miles": safety_search_miles,
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
        # What TxDOT publishes about the road itself, from ``roadway.block``.
        # It was a constant here until 2026-09-19, saying the facts came from a
        # service this tool did not call. They come from the records the
        # alignment step already fetched, so this block costs no request.
        # [#183](https://github.com/RickSmith/survey-recon/issues/183).
        # The wording is ``roadway.block``'s own default, repeated rather than
        # imported: that module reads ``not_screened`` from this one, so this
        # one cannot read from it. The command line always passes a block, so
        # this branch is a net under callers that do not.
        "roadway": roadway if roadway is not None else not_screened(
            "the run did not reach the route service"
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
        # Where the nearest help is, from ``safety.block``. Kept apart from the
        # parcel rows on purpose: issue #18 is blunt that this is a different
        # output, answering a party chief's question rather than a bid one. A
        # hospital does not belong in a column of things that cost days of
        # notice.
        "crew_safety": crew_safety if crew_safety is not None else not_screened(
            "the run did not reach the crew safety step"
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
