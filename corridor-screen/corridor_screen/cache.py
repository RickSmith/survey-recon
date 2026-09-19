"""Saved copies of answers, with a record of where each one came from.

Every response this tool receives is written to disk exactly as the server
sent it, beside a second file saying when it was captured and what was asked
for. The reasoning is in ``docs/corridor-screen/spec.md`` section 14, and the
load-bearing sentence is this one: the response file is never edited. The
moment provenance is written into a response, "this is real data the server
really sent" stops being true.

Layout, under the output directory::

    cache/
      <service>/
        <readable-name>__<short-hash>.json        what the server sent
        <readable-name>__<short-hash>.meta.toml   where it came from
      INDEX.md                                    one line per response

TOML is a plain text settings format meant for people to read. Python reads it
with nothing installed, and it carries comments, which matters when a human
may need to read a capture record on stage.
"""

import hashlib
import json
import os
import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path

INDEX_NAME = "INDEX.md"

# The heading of that file, without a corridor on it. Named once because
# `write_index` both writes it and reads it back to see whether the line
# already there is this file's heading or somebody else's text.
PLAIN_INDEX_HEADING = "# Cached responses"

# Windows refuses to open a path longer than 260 characters unless it is asked
# in the extended form. A surveyor working under
# "OneDrive - Some Long Firm Name\Documents\Projects\..." reaches that
# limit easily, and the failure is a file-not-found error on a directory that
# plainly exists -- confusing enough to sink an afternoon. Every read and write
# in this file goes through long_path, so the cache works wherever the project
# happens to sit.
LONG_PATH_PREFIX = "\\\\?\\"


def long_path(path):
    """The form of a path that Windows will open at any length."""
    absolute = os.path.abspath(str(path))
    if os.name == "nt" and not absolute.startswith(LONG_PATH_PREFIX):
        return LONG_PATH_PREFIX + absolute
    return absolute


def _short_hash(method, url, params):
    """A stable short name for one exact request.

    Parameters are sorted before hashing so that the same request asked twice
    lands on the same cache file, whatever order the parameters were built in.
    """
    payload = json.dumps(
        {"method": method.upper(), "url": url, "params": {k: str(v) for k, v in sorted(params.items())}},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def slug(text):
    """Squeeze a label down to something safe to use as a file name."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", str(text)).strip("-").lower()
    return cleaned[:40] or "response"


def _toml_value(value):
    """Render one value as TOML.

    Deliberately small. It covers strings, numbers, booleans, and flat lists of
    those, which is everything a provenance record holds. Anything else is
    turned into a string rather than guessed at.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        # TOML has a real date type. Written bare rather than quoted, so a
        # timestamp missing its time zone fails when the record is read back
        # instead of sitting there looking like a time.
        return value.isoformat(timespec="seconds")
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return '"' + escaped + '"'


def render_toml(table, sub_tables=None):
    """Render a flat table, optionally followed by named sub-tables."""
    lines = [f"{k} = {_toml_value(v)}" for k, v in table.items()]
    for name, sub in (sub_tables or {}).items():
        lines.append("")
        lines.append(f"[{name}]")
        lines.extend(f"{k} = {_toml_value(v)}" for k, v in sub.items())
    return "\n".join(lines) + "\n"


class CacheEntry:
    """Where one response lives, and what request it answers."""

    def __init__(self, root, service, readable, method, url, params):
        self.service = service
        self.readable = slug(readable)
        self.method = method.upper()
        self.url = url
        self.params = dict(params)
        self.key = _short_hash(method, url, params)
        self.directory = Path(root) / slug(service)
        self.stem = f"{self.readable}__{self.key}"
        # Filled in when a response is saved, so that a sanity check tripping
        # later can be written into the record without re-reading it.
        self.captured_at = None
        self.provenance = None

    @property
    def body_path(self):
        return self.directory / f"{self.stem}.json"

    @property
    def meta_path(self):
        return self.directory / f"{self.stem}.meta.toml"

    @property
    def cache_key(self):
        """How the output file points at this response."""
        return f"{slug(self.service)}/{self.stem}"

    def exists(self):
        return os.path.exists(long_path(self.body_path))


class Cache:
    """The cache directory for one screening run."""

    def __init__(self, root):
        self.root = Path(root)

    def entry(self, service, readable, url, params, method="GET"):
        return CacheEntry(self.root, service, readable, method, url, params)

    def read(self, entry):
        """The bytes the server sent, or None if this request was never made."""
        if not entry.exists():
            return None
        with open(long_path(entry.body_path), "rb") as handle:
            return handle.read()

    def read_meta(self, entry):
        """The provenance record of a saved response, as a table, or None."""
        if not os.path.exists(long_path(entry.meta_path)):
            return None
        return tomllib.loads(read_text(entry.meta_path))

    def captured_at_of(self, entry):
        """When a cached response was captured.

        Reading it back also restores the record onto the entry, so that a
        sanity check tripping on replayed data can still be written down. A run
        served from the cache must be able to say how old its data is -- that
        is the whole point of the honesty block.
        """
        record = self.read_meta(entry)
        if not record:
            return None
        # "warnings" is rewritten on every visit and "request_params" is its own
        # sub-table, so neither belongs in the flat part of the record.
        entry.provenance = {
            k: v for k, v in record.items() if k not in ("warnings", "request_params")
        }
        captured = record.get("captured_at")
        entry.captured_at = captured
        return captured.isoformat(timespec="seconds") if hasattr(captured, "isoformat") else captured

    def write(self, entry, body, http_status, layer_id=None, record_count=None, warnings=()):
        """Save a response and its provenance record.

        The response goes down untouched. Everything known about how it was
        obtained goes in the second file beside it.
        """
        os.makedirs(long_path(entry.directory), exist_ok=True)
        with open(long_path(entry.body_path), "wb") as handle:
            handle.write(body)
        entry.captured_at = datetime.now(timezone.utc).astimezone()
        entry.provenance = {
            "service": entry.service,
            "cache_key": entry.cache_key,
            "request_method": entry.method,
            "request_url": entry.url,
            "captured_at": entry.captured_at,
            "http_status": int(http_status),
            "response_bytes": len(body),
            "layer_id": int(layer_id) if layer_id is not None else None,
            "record_count": int(record_count) if record_count is not None else None,
        }
        self._write_provenance(entry, warnings)

    def add_warnings(self, entry, warnings):
        """Record, beside a response already saved, what was doubted about it.

        Sanity checks run after a response is in hand, so this is a second
        visit to the provenance record -- section 14 asks it to carry "any
        sanity check that tripped". The response file is not touched, only the
        record beside it.
        """
        if not warnings or not entry.provenance:
            return
        self._write_provenance(entry, warnings)

    def _write_provenance(self, entry, warnings):
        table = {k: v for k, v in entry.provenance.items() if v is not None}
        table["warnings"] = [w["check"] if isinstance(w, dict) else str(w) for w in warnings]
        header = (
            "# Provenance record. The response file beside this one is exactly what the\n"
            "# server sent and is never edited. Every parameter of the request is listed\n"
            "# under [request_params], so the call can be repeated and checked.\n"
        )
        write_text(entry.meta_path, header + render_toml(table, {"request_params": entry.params}))

    def entries(self):
        """Every provenance record in the cache, oldest name first."""
        return sorted(self.root.glob("*/*.meta.toml"))

    def _heading_on_disk(self):
        """The heading the index already carries, or ``None`` if there is none.

        ``None`` covers three cases that are all the same answer: no index yet,
        an empty one, and one whose first line is not this file's heading.
        Junk in the file is not a corridor, and carrying it forward would
        spread it rather than contain it.
        """
        path = self.root / INDEX_NAME
        if not os.path.exists(long_path(path)):
            return None
        lines = read_text(path).splitlines()
        first = lines[0].strip() if lines else ""
        return first if first.startswith(PLAIN_INDEX_HEADING) else None

    def write_index(self, corridor_label=None):
        """Regenerate INDEX.md -- the file you point at when you say the
        captures are from a particular date.

        **A caller with no label to give, and a cache with no corridor, are not
        the same claim.** They used to be: the label defaulted to the empty
        string and was tested for truth, so both blanked the heading.

        Two commands write this file. The screening run knows the corridor. The
        live NGS check does not, passed nothing, and so asserted that there was
        none. The corridor went missing from the heading on 2026-09-13 and
        stayed missing on ``main`` until 2026-09-19 -- six days, through several
        reviews -- and came back only because a screening run happened to
        rewrite it. Every rehearsal runs the live check, so the wrong version
        won whenever it went last. [#186](https://github.com/RickSmith/survey-recon/issues/186).

        So the three are now three:

        * ``None`` -- nothing to say about the corridor. Keep the heading that
          is there. This is the live check
        * a label -- use it, and overwrite whatever was there. This is the
          screening run, including on a folder rerun for a different corridor
        * ``""`` -- there is no corridor, said deliberately. Plain heading

        **This is the same distinction three other parts of this tool draw**,
        and it is worth knowing them together. A county road with no published
        ``ROW_MIN`` is not a road with no right of way. A ROW sheet with no
        drawing is not a sheet nobody can reach. A field a layer stopped
        publishing is not a field with no values. Absent and unstated are
        different, and a default that conflates them is this bug.

        The rows are always rebuilt, whatever happens to the heading. That is
        the whole reason the live check regenerates this at all: writing a
        response without regenerating leaves the index quietly wrong about it.
        """
        rows = []
        for meta_path in self.entries():
            data = tomllib.loads(read_text(meta_path))
            rows.append(
                "| {service} | {layer} | {captured} | {count} | `{key}` |".format(
                    service=data.get("service", "?"),
                    layer=data.get("layer_id", "-"),
                    captured=data.get("captured_at", "?"),
                    count=data.get("record_count", "-"),
                    key=data.get("cache_key", meta_path.stem),
                )
            )
        if corridor_label is None:
            heading = self._heading_on_disk() or PLAIN_INDEX_HEADING
        elif corridor_label:
            heading = f"{PLAIN_INDEX_HEADING} -- {corridor_label}"
        else:
            heading = PLAIN_INDEX_HEADING
        text = "\n".join(
            [
                heading,
                "",
                "Every response this tool received, saved exactly as the server sent it.",
                "The `.meta.toml` file beside each one carries the full request.",
                "",
                "| Service | Layer | Captured | Records | Cache key |",
                "|---|---|---|---|---|",
                *rows,
                "",
            ]
        )
        os.makedirs(long_path(self.root), exist_ok=True)
        write_text(self.root / INDEX_NAME, text)
        return self.root / INDEX_NAME


def read_text(path):
    with open(long_path(path), "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, text):
    with open(long_path(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
