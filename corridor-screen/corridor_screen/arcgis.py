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
from datetime import datetime, timedelta, timezone

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


def attribute(attributes, name):
    """Read one field out of a returned feature, whatever case it answered in.

    The trap this exists for is recorded at the bottom of ``sources.py``: the
    USGS structures layers publish their fields as ``NAME`` and
    ``PERMANENT_IDENTIFIER`` and then answer a query with ``name`` and
    ``permanent_identifier``. A plain dictionary lookup finds nothing, raises
    nothing, and every school comes out unnamed.

    A blank string from a database is an absent value, not an empty answer.
    The NGS datasheets service publishes a single space for a condition nobody
    has recorded, and read carelessly that is a non-empty string.

    It lives here rather than with either of the things that read features,
    because both of them read features from ArcGIS and neither owns the trap.
    """
    attributes = attributes or {}
    if name in attributes:
        value = attributes[name]
    else:
        wanted = name.lower()
        value = next((v for k, v in attributes.items() if k.lower() == wanted), None)
    if isinstance(value, str):
        return value.strip() or None
    return value


# Milliseconds since here is what an ArcGIS date field carries.
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def from_epoch_ms(value):
    """One ArcGIS date field, as a date a person can read.

    **The trap, and it does not return a wrong answer -- it stops the run.**
    A service that publishes a real date field sends it as milliseconds since
    1970, so anything older than 1970 is a **negative** number. Handed to
    ``datetime.fromtimestamp`` or ``datetime.utcfromtimestamp`` on Windows, a
    negative value raises ``OSError: [Errno 22] Invalid argument``. Confirmed
    on Windows 11 with Python 3.11 on 2026-09-12, on the real value TxDOT's ROW
    map service returns for its 1937 sheet. Adding a ``timedelta`` to the epoch
    has no such limit.

    Anything that is not a number is passed through exactly as it arrived. A
    value this code does not recognize is not a value it should be rewriting,
    which is the same trade ``control._recovered_on`` already makes.

    It lives here, beside ``attribute``, for the reason written above that
    function: both are about reading what an ArcGIS service actually sent, and
    two services now need this one. TxDOT's ROW map sheets publish ``MAP_FROM_DT``
    and the USGS structures layers publish ``LOADDATE``, and neither module
    owns the trap.
    """
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    return (EPOCH + timedelta(milliseconds=value)).date().isoformat()


def from_compact_date(value):
    """``20020308`` written out as ``2002-03-08``.

    NGS publishes its recovery dates as eight digits in a string, on both of
    the endpoints this tool calls -- ``LAST_RECV`` on the datasheets feature
    service and ``lastRecovered`` on the Data Explorer API. On a projector,
    eight digits read as a number rather than a date.

    Anything this does not recognize is passed through exactly as it arrived. A
    value this code cannot read is not a value it should be rewriting.

    It lives here beside ``attribute`` and ``from_epoch_ms``, for the reason
    written above those: all three are about reading what a service actually
    sent, two callers need this one, and neither of them owns it.
    """
    if isinstance(value, str) and len(value) == 8 and value.isdigit():
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
    return value


def error_of(data):
    """The error a service reported *inside* a successful HTTP response.

    Returns a readable message, or ``None`` when the body is a real answer.

    **An ArcGIS service can fail without failing.** It answers ``HTTP 200`` and
    puts the problem in the body, so the status line says everything is fine.
    Read on 2026-09-13, the Railroad Commission's pipeline service was serving
    this, with a 200 in front of it::

        {"error": {"code": 503, "message": "User couldn't access this
         resource 'rrc_public/tpms.mapserver'.", "details": []}}

    Both the ping and ``get_json`` have to ask this question, and only one of
    them used to. That asymmetry is issue #62: the ping waved the host through
    as answering, and saved the error body over a good capture on its way past.

    A body that is not a JSON object -- a list of NGS marks, a line of plain
    text -- carries no such block and is not an error by this test.

    **The answer is never an empty string.** An ``error`` block with nothing
    readable in it is still an error, and returning ``""`` for one would make
    every caller's ``if reported:`` quietly wave it through. That is how the
    first attempt at this function reintroduced the bug it was written to fix.

    The status line is deliberately **not** named here. This function is handed
    the body and never sees the status, so it is in no position to state one.
    A caller that knows the real status says so itself.
    """
    if not isinstance(data, dict) or "error" not in data:
        return None
    error = data.get("error") or {}
    code = error.get("code")
    details = "; ".join(str(d) for d in (error.get("details") or []))
    said = f"{error.get('message', '')} {details}".strip()
    if code is not None:
        return f"error {code}: {said}" if said else f"error {code}"
    return said or "an error with no message"


def _json_or_none(body):
    """The body as data, or ``None`` if it is not JSON at all."""
    try:
        return json.loads(body)
    except (ValueError, TypeError):
        return None


def _encode(params):
    return urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})


def _describe_url(source):
    """The address whose own description of itself answers both questions.

    The reachability ping and the field list check ask a layer the same thing:
    "describe yourself". Naming that request once means it is cached once, so
    the field list check costs no second call, and the index does not carry two
    files holding identical bytes.
    """
    url = source.layer_url if source.layer_id is not None else source.base_url
    name = (
        f"{source.name}-layer-{source.layer_id}-metadata"
        if source.layer_id is not None
        else f"{source.name}-metadata"
    )
    return url, name, {"f": "json"}


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
        # Every cache entry this run touched, by cache key, so that a sanity
        # check tripping later can be written back into the right record.
        self.entries = {}

    def note_warnings(self, records, warnings):
        """Write tripped checks into the provenance of the responses they doubt."""
        for record in records:
            entry = self.entries.get(record["cache_key"])
            if entry is not None:
                self.cache.add_warnings(entry, warnings)

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
        url, readable, params = _describe_url(source)
        started = time.monotonic()
        try:
            body, status = _open(url, params, "GET", PING_TIMEOUT_S)
        except Exception as exc:
            elapsed = int((time.monotonic() - started) * 1000)
            return {"ping": "blocked", "ms": elapsed, "detail": f"{type(exc).__name__}: {exc}"}
        elapsed = int((time.monotonic() - started) * 1000)

        # **The body decides, not the status line.** A service can answer 200
        # and put a 503 in the payload, and a ping that only watched the
        # transport would call that host healthy. It is not: it is serving
        # nothing, and the run needs to know now rather than at the field-list
        # check ninety seconds later. Issue #62.
        #
        # A body can fail to be an answer in two ways, and both are checked.
        # It can carry an error block, which is what the Railroad Commission
        # served. Or it can not be JSON at all -- an HTML error page from a
        # gateway, or the plain text a wrong `wkid` produces. Every source is
        # pinged with `f=json` for a layer description, so a body that will not
        # parse is a host that is not answering either.
        data = _json_or_none(body)
        reported = error_of(data) if data is not None else (
            f"a body that is not JSON at all: {body[:120]!r}"
        )
        if reported:
            # **Saved, and this is the part worth weighing.** Issue #62 offered
            # three directions and asked for none of them to be picked in
            # silence, so all three are answered here.
            #
            # *Do not write at all, since a cached ping is never served.* True
            # of the ping result, false of the response. `layer_metadata` reads
            # this exact request back out of the cache -- it is why a cache-only
            # run can check a field list at all -- so a ping that wrote nothing
            # would break every offline run rather than one poisoned one.
            #
            # *Refuse to overwrite a good response with an error one.* Correct
            # in effect, but it protects the second run and not the first. A
            # corridor captured for the first time during an outage would still
            # be left with an error body sitting at the name a later run treats
            # as the capture.
            #
            # *Write it under a distinct key.* Taken. Section 14 says every
            # response is saved, the failure is a response, and under its own
            # name it can neither be mistaken for a capture nor destroy one.
            # The prefix leads rather than trails because `slug` truncates at
            # 40 characters, so a `-error` suffix would collide with the very
            # name it was meant to differ from.
            reported = f"HTTP {status} carrying {reported}"
            # The warning is not decoration. The provenance record beside this
            # body will say `http_status = 200`, which is true and is the whole
            # trap. Somebody reading that file a month from now should not have
            # to infer the failure from a filename.
            failed = self.cache.entry(source.name, f"error-{readable}", url, params)
            self.cache.write(
                failed, body, status, layer_id=source.layer_id, warnings=[reported]
            )
            self.entries[failed.cache_key] = failed
            return {
                "ping": "blocked",
                "ms": elapsed,
                "detail": reported,
                "cache_key": failed.cache_key,
            }

        # The ping answer is a response like any other, so it is saved like any
        # other. It is never served *from* the cache -- a cached ping would say
        # a host was reachable last week, which is not what a ping is for.
        entry = self.cache.entry(source.name, readable, url, params)
        self.cache.write(entry, body, status, layer_id=source.layer_id)
        self.entries[entry.cache_key] = entry
        return {
            "ping": "slow" if elapsed >= SLOW_PING_MS else "ok",
            "ms": elapsed,
            "detail": "",
            "cache_key": entry.cache_key,
        }

    # -- fetching ----------------------------------------------------------

    def get_json(self, source_name, readable, url, params, method="GET", layer_id=None, count_records=None):
        """Ask for one response, from the cache or from the network.

        Returns ``(data, record)``. The record is the provenance of this one
        call, which the honesty block in the output is built from.

        **This function is the only place in the tool where live and replayed
        runs differ, and that is the whole design.** Everything above it --
        every query, every filter, every count, every warning -- runs the same
        code and cannot tell which it got. There is no replay mode of the tool;
        there is one tool, and one function that decides where a response comes
        from. That is what issue #19 means by "the live and cached paths share
        the same logic," and it is why a cache-only run is a replay rather than
        a recording.

        The record carries ``status: from-cache`` and the capture date, so a
        replayed run says how old its data is rather than implying it is fresh.
        ``corridor_screen.replay`` is the check that the two really do agree.
        """
        entry = self.cache.entry(source_name, readable, url, params, method=method)
        cached = self.cache.read(entry) if self.mode != "live" else None

        if cached is not None:
            data = json.loads(cached)
            self.entries[entry.cache_key] = entry
            record = {
                "cache_key": entry.cache_key,
                "status": "from-cache",
                "attempts": 0,
                "http_status": None,
                "captured_at": self.cache.captured_at_of(entry),
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
        reported = error_of(data)
        if reported:
            raise ServiceError(f"{source_name}: {reported}")

        count = count_records(data) if callable(count_records) else None
        self.cache.write(entry, body, status, layer_id=layer_id, record_count=count)
        self.entries[entry.cache_key] = entry
        record = {
            "cache_key": entry.cache_key,
            "status": "ok",
            "attempts": attempts,
            "http_status": status,
            "captured_at": entry.captured_at.isoformat(timespec="seconds"),
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
        """The layer's own description of itself, including its field list.

        In every mode but `live` this is already on disk, because the ping a
        moment ago asked the same question and saved the answer.
        """
        url, readable, params = _describe_url(source)
        return self.get_json(source.name, readable, url, params, layer_id=source.layer_id)

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
