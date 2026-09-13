"""Asking ArcGIS services questions, and saving what they say.

Nothing here is installed. ``urllib`` from the standard library does the work,
which is what lets the whole tool run on a machine with Python and nothing
else.

Two rules from the specification shape this file.

Section 7 -- **a dead service stops the run.** Three automatic retries with a
growing wait, because most blocks are momentary. Then a person decides, if a
person is there. If nobody is at the keyboard the run exits rather than waits,
because a tool that hangs forever in an unattended run is a broken tool.

Section 14 -- **every response is saved.** The caller never sees a response
that was not written to disk with its provenance record first.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "survey-recon corridor-screen (https://github.com/RickSmith/survey-recon)"

MODES = ("live", "cache-first", "cache-only")

PING_TIMEOUT_S = 8
SLOW_PING_MS = 2000


class ServiceDown(Exception):
    """A service was asked and did not answer, after every retry."""

    def __init__(self, service, detail, attempts):
        super().__init__(f"{service}: {detail}")
        self.service = service
        self.detail = detail
        self.attempts = attempts


class ServiceError(Exception):
    """A service answered, but the answer was an error message.

    Kept apart from ``ServiceDown`` on purpose. A host that is blocking today
    may work in ten minutes. A query the server rejects will be rejected again
    however long you wait, so retrying it is only a slower way to fail.
    """


def _encode(params):
    return urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})


def _open(url, params, method, timeout):
    """One request. Returns the raw bytes and the HTTP status."""
    encoded = _encode(params)
    if method.upper() == "POST":
        request = urllib.request.Request(url, data=encoded.encode("utf-8"))
    else:
        request = urllib.request.Request(f"{url}?{encoded}" if encoded else url)
    request.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(), response.status


class Fetcher:
    """Every call to every service goes through here."""

    def __init__(self, cache, mode="cache-first", timeout=90, retries=3):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, not {mode!r}")
        self.cache = cache
        self.mode = mode
        self.timeout = timeout
        self.retries = retries

    # -- reachability ------------------------------------------------------

    def ping(self, source):
        """A cheap check that a host is answering today.

        This exists because last is not soon enough to find out. Our own
        research recorded maps.dot.state.tx.us failing and then succeeding
        minutes later. Seconds spent here save a run abandoned ninety seconds
        in.
        """
        if self.mode == "cache-only":
            return {"ping": "skipped", "ms": 0, "detail": "cache-only run makes no network calls"}
        url = source.layer_url if source.layer_id is not None else source.base_url
        started = time.monotonic()
        try:
            _open(url, {"f": "json"}, "GET", PING_TIMEOUT_S)
        except Exception as exc:
            elapsed = int((time.monotonic() - started) * 1000)
            return {"ping": "blocked", "ms": elapsed, "detail": f"{type(exc).__name__}: {exc}"}
        elapsed = int((time.monotonic() - started) * 1000)
        return {"ping": "slow" if elapsed >= SLOW_PING_MS else "ok", "ms": elapsed, "detail": ""}

    # -- fetching ----------------------------------------------------------

    def get_json(self, source_name, readable, url, params, method="GET", layer_id=None, count_records=None):
        """Ask for one response, from the cache or from the network.

        Returns ``(data, record)``. The record is the provenance of this one
        call, which the honesty block in the output is built from.
        """
        entry = self.cache.entry(source_name, readable, url, params, method=method)
        cached = self.cache.read(entry) if self.mode != "live" else None

        if cached is not None:
            data = json.loads(cached)
            record = {
                "cache_key": entry.cache_key,
                "status": "from-cache",
                "attempts": 0,
                "http_status": None,
            }
            return data, record

        if self.mode == "cache-only":
            raise ServiceDown(
                source_name,
                "no cached response for this request ("
                + entry.cache_key
                + "); run once in cache-first mode to capture it",
                attempts=0,
            )

        body, status, attempts = self._fetch_with_retries(source_name, url, params, method)
        data = json.loads(body)
        if isinstance(data, dict) and "error" in data:
            message = data["error"].get("message", "unknown error")
            details = "; ".join(data["error"].get("details", []) or [])
            raise ServiceError(f"{source_name}: {message} {details}".strip())

        count = count_records(data) if callable(count_records) else None
        self.cache.write(entry, body, status, layer_id=layer_id, record_count=count)
        record = {
            "cache_key": entry.cache_key,
            "status": "ok",
            "attempts": attempts,
            "http_status": status,
        }
        return data, record

    def _fetch_with_retries(self, source_name, url, params, method):
        """Three tries with a growing wait. Most blocks are momentary."""
        wait = 1.0
        last = None
        for attempt in range(1, self.retries + 1):
            try:
                body, status = _open(url, params, method, self.timeout)
                return body, status, attempt
            except urllib.error.HTTPError as exc:
                last = f"HTTP {exc.code} {exc.reason}"
            except Exception as exc:
                last = f"{type(exc).__name__}: {exc}"
            if attempt < self.retries:
                time.sleep(wait)
                wait *= 2
        raise ServiceDown(source_name, last or "no answer", attempts=self.retries)

    # -- queries -----------------------------------------------------------

    def layer_metadata(self, source):
        """The layer's own description of itself, including its field list."""
        return self.get_json(
            source.name,
            f"{source.name}-layer-{source.layer_id}-metadata",
            source.layer_url,
            {"f": "json"},
            layer_id=source.layer_id,
        )

    def query_all(self, source, params, readable, page_size=2000):
        """Every feature matching a query, one page at a time.

        ArcGIS caps how many records it will return at once. Asking for more
        than the cap does not error -- it returns the cap and sets a flag, and
        a tool that ignores the flag reports a paging limit as if it were an
        answer. That trap is one of the sanity checks in ``checks.py``; this
        loop is how the trap is avoided in the first place.
        """
        features = []
        records = []
        offset = 0
        while True:
            page = dict(params)
            page["resultOffset"] = offset
            page["resultRecordCount"] = page_size
            data, record = self.get_json(
                source.name,
                f"{readable}-offset-{offset}",
                source.query_url,
                page,
                method="POST",
                layer_id=source.layer_id,
                count_records=lambda d: len(d.get("features", [])),
            )
            records.append(record)
            batch = data.get("features", [])
            features.extend(batch)
            if not data.get("exceededTransferLimit") or not batch:
                break
            offset += len(batch)
        return features, records
