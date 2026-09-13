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
from datetime import datetime, timezone
from pathlib import Path

INDEX_NAME = "INDEX.md"

# Windows refuses to open a path longer than 260 characters unless it is asked
# in the extended form. A surveyor working under
# "OneDrive - Some Long Firm Name\Documents\Projects\..." reaches that
# limit easily, and the failure is a file-not-found error on a directory that
# plainly exists -- confusing enough to sink an afternoon. Every read and write
# in this file goes through _long_path, so the cache works wherever the project
# happens to sit.
LONG_PATH_PREFIX = "\\\\?\\"


def _long_path(path):
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


def _slug(text):
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
    escaped = escaped.replace("\n", "\n").replace("\r", "\r").replace("\t", "\t")
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
        self.readable = _slug(readable)
        self.method = method.upper()
        self.url = url
        self.params = dict(params)
        self.key = _short_hash(method, url, params)
        self.directory = Path(root) / _slug(service)
        self.stem = f"{self.readable}__{self.key}"

    @property
    def body_path(self):
        return self.directory / f"{self.stem}.json"

    @property
    def meta_path(self):
        return self.directory / f"{self.stem}.meta.toml"

    @property
    def cache_key(self):
        """How the output file points at this response."""
        return f"{_slug(self.service)}/{self.stem}"

    def exists(self):
        return os.path.exists(_long_path(self.body_path))


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
        with open(_long_path(entry.body_path), "rb") as handle:
            return handle.read()

    def read_meta(self, entry):
        if not entry.meta_path.exists():
            return None
        return _read_text(entry.meta_path)

    def write(self, entry, body, http_status, layer_id=None, record_count=None, warnings=()):
        """Save a response and its provenance record.

        The response goes down untouched. Everything known about how it was
        obtained goes in the sidecar beside it.
        """
        os.makedirs(_long_path(entry.directory), exist_ok=True)
        with open(_long_path(entry.body_path), "wb") as handle:
            handle.write(body)
        table = {
            "service": entry.service,
            "cache_key": entry.cache_key,
            "request_method": entry.method,
            "request_url": entry.url,
            "captured_at": datetime.now(timezone.utc).astimezone(),
            "http_status": int(http_status),
            "response_bytes": len(body),
        }
        if layer_id is not None:
            table["layer_id"] = int(layer_id)
        if record_count is not None:
            table["record_count"] = int(record_count)
        table["warnings"] = list(warnings)
        header = (
            "# Provenance record. The response file beside this one is exactly what the\n"
            "# server sent and is never edited. Every parameter of the request is listed\n"
            "# under [request_params], so the call can be repeated and checked.\n"
        )
        body_text = render_toml(table, {"request_params": entry.params})
        _write_text(entry.meta_path, header + body_text)

    def entries(self):
        """Every provenance record in the cache, oldest name first."""
        return sorted(self.root.glob("*/*.meta.toml"))

    def write_index(self, corridor_label=""):
        """Regenerate INDEX.md -- the file you point at when you say the
        captures are from a particular date."""
        import tomllib

        rows = []
        for meta_path in self.entries():
            data = tomllib.loads(_read_text(meta_path))
            rows.append(
                "| {service} | {layer} | {captured} | {count} | `{key}` |".format(
                    service=data.get("service", "?"),
                    layer=data.get("layer_id", "-"),
                    captured=data.get("captured_at", "?"),
                    count=data.get("record_count", "-"),
                    key=data.get("cache_key", meta_path.stem),
                )
            )
        heading = "# Cached responses"
        if corridor_label:
            heading += f" -- {corridor_label}"
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
        os.makedirs(_long_path(self.root), exist_ok=True)
        _write_text(self.root / INDEX_NAME, text)
        return self.root / INDEX_NAME


def _read_text(path):
    with open(_long_path(path), "r", encoding="utf-8") as handle:
        return handle.read()


def _write_text(path, text):
    with open(_long_path(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
