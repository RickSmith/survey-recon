"""Reading the lead-time table, and refusing to read a bad one.

The table itself is ``lead_times.toml`` beside this file. It is data, not code,
because a number with legal consequence should be editable by the person who
is accountable for it without touching Python, and should show a readable diff
when it changes.

This module does three things and nothing else.

**It refuses to load a row without a citation.** A lead time with no source is
a rumor with a number on it, and one of those in front of a licensed surveyor
is worse than no tool at all. This is a hard error, for the same reason the
field list check is a hard error: it is a configuration mistake, and it costs
nothing to catch before the run rather than after.

**It keeps "not confirmed" separate from "no delay".** A row with no
``lead_time_days`` is not a row that costs nothing. It is a row where we looked
and did not find a published figure, and it carries the account of where we
looked. That account travels into the output, so a reader sees "not found"
rather than a blank.

**It hands back a flat record per flag type**, so that attaching a lead time to
a flag is a dictionary lookup rather than a rule.
"""

import tomllib
from pathlib import Path

TABLE_PATH = Path(__file__).with_name("lead_times.toml")

# Every row must carry these. See the module docstring: a lead time without a
# citation does not go in front of a surveyor.
REQUIRED = ("label", "source", "url", "driver")

# A row that claims a number must say where the number came from and whether it
# is statute or somebody's published procedure. Those are different kinds of
# promise and an estimator reads them differently.
REQUIRED_WHEN_CONFIRMED = ("lead_time_days", "statutory", "verified_on", "basis")

# A number of days is meaningless without saying which days. Two working days
# and two calendar days are different promises, and § 251.151(a) means the
# first while § 711.041 means the second.
BASES = ("calendar days", "working days")

# A row that has no number must say where it looked. "Not found" without that
# is indistinguishable from not having tried.
REQUIRED_WHEN_NOT_CONFIRMED = ("not_found",)


class LeadTimeTableError(Exception):
    """The lead-time table is not fit to quote. Nothing after this is safe."""


class LeadTime:
    """One row of the table: what a flag type costs, and who says so."""

    def __init__(self, key, row):
        self.key = key
        self.label = row["label"]
        self.screenable = bool(row.get("screenable", False))
        self.confirmed = bool(row.get("confirmed", False))
        self.statutory = bool(row.get("statutory", False))
        self.days = row.get("lead_time_days")
        # Only where the published figure is a range. The planning number is
        # the top of it; this is the bottom, kept so a reader can see the range
        # the tool chose from rather than only the choice.
        self.days_low = row.get("lead_time_days_low")
        # Which days. See BASES -- this is never guessed and never converted.
        self.basis = row.get("basis")
        self.driver = row["driver"]
        self.source = row["source"]
        self.url = row["url"]
        self.verified_on = row.get("verified_on")
        self.note = _tidy(row.get("note"))
        self.not_found = _tidy(row.get("not_found"))

    def describe(self):
        """The lead-time part of a flag, in the shape the output file uses.

        ``lead_time_days`` is ``None`` where no figure was confirmed, and
        ``lead_time_not_found`` then carries the account of where we looked.
        The two are never both filled and never both empty.
        """
        return {
            "lead_time_days": self.days,
            "lead_time_days_low": self.days_low,
            "lead_time_basis": self.basis,
            "lead_time_confirmed": self.confirmed,
            "lead_time_statutory": self.statutory,
            "lead_time_driver_detail": self.driver,
            "lead_time_source": self.source,
            "lead_time_url": self.url,
            "lead_time_verified_on": str(self.verified_on) if self.verified_on else None,
            "lead_time_note": self.note,
            "lead_time_not_found": self.not_found,
        }


def _tidy(text):
    """Fold a TOML multi-line string back into one readable line."""
    if text is None:
        return None
    return " ".join(str(text).split()) or None


def _check(key, row):
    missing = [name for name in REQUIRED if not row.get(name)]
    needed = REQUIRED_WHEN_CONFIRMED if row.get("confirmed") else REQUIRED_WHEN_NOT_CONFIRMED
    missing += [name for name in needed if row.get(name) in (None, "")]
    if missing:
        raise LeadTimeTableError(
            f"lead-time row [{key}] is missing {', '.join(sorted(set(missing)))}. "
            "Every row must carry a source and a link. A confirmed row must carry "
            "its number, say which days that number counts, and say whether it is "
            "statutory. An unconfirmed row must say where it looked. A lead time "
            "without a citation is a rumor with a number on it."
        )
    if row.get("confirmed") and row.get("basis") not in BASES:
        raise LeadTimeTableError(
            f"lead-time row [{key}] gives a number of days without saying which "
            f"days. `basis` must be one of {', '.join(BASES)}. Two working days "
            "and two calendar days are different promises."
        )
    if row.get("confirmed") and row.get("not_found"):
        raise LeadTimeTableError(
            f"lead-time row [{key}] is marked confirmed and also carries a "
            "not_found account. One of those is wrong, and a reader cannot tell "
            "which."
        )
    if not row.get("confirmed"):
        account = _tidy(row.get("not_found")) or ""
        # CLAUDE.md: write "not found" rather than "does not exist," and say
        # where you looked. Checked here rather than trusted, because the row
        # that forgets is the one a reader will take for "no delay".
        if not account.lower().startswith("not found"):
            raise LeadTimeTableError(
                f"lead-time row [{key}] has no confirmed number, so its "
                "not_found account must begin with the words \"Not found\". "
                "Anything softer reads as no delay."
            )
        if "looked in" not in account.lower() and "look for" not in account.lower():
            raise LeadTimeTableError(
                f"lead-time row [{key}] says not found without saying where it "
                "looked. \"Not found\" with no account of the search is "
                "indistinguishable from not having tried."
            )


def load(path=None):
    """Read the table. Raises rather than returning a table that cannot be quoted."""
    path = Path(path or TABLE_PATH)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LeadTimeTableError(f"the lead-time table is missing from {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise LeadTimeTableError(f"the lead-time table at {path} is not readable TOML: {exc}") from exc

    table = {}
    for key, row in data.items():
        if not isinstance(row, dict):
            continue  # schema_version and anything else at the top level
        _check(key, row)
        table[key] = LeadTime(key, row)
    if not table:
        raise LeadTimeTableError(f"the lead-time table at {path} has no rows")
    return table


def longest(flags):
    """The biggest confirmed lead time among some flags, and what set it.

    Returns ``(days, driver_type, basis)``, or ``(None, None, None)`` when
    nothing on the parcel carries a confirmed figure.

    This exists so that the longest wait on a parcel is a number somebody can
    read, rather than something they work out by scanning a list. A parcel you
    cannot enter for 45 days is a schedule problem the day you bid.

    **The basis comes back with the number, and the number is never converted.**
    Two working days and two calendar days are different promises, and turning
    one into the other would mean inventing a calendar of weekends and Texas
    legal holidays that this tool does not have and could not check. So the
    biggest published figure wins and it is always reported saying which days
    it counts. A reader who sees "2 working days" knows to add the weekend
    themselves. A reader who sees a bare "2" does not.
    """
    numbered = [f for f in flags if isinstance(f.get("lead_time_days"), (int, float))]
    if not numbered:
        return None, None, None
    worst = max(numbered, key=lambda f: f["lead_time_days"])
    return worst["lead_time_days"], worst["type"], worst.get("lead_time_basis")


def unconfirmed_types(flags):
    """Flag types on a parcel whose lead time could not be confirmed.

    Kept beside ``longest`` and reported beside it, because a parcel whose only
    flag is a school would otherwise show no number and read as if it were
    clear. It is not clear. It is unmeasured, which is a different thing, and
    it is the same distinction as ``unknown`` against ``no``.
    """
    return sorted({f["type"] for f in flags if f.get("lead_time_days") is None})


def cite(entry):
    """One row's number and its citation, for the output file.

    Carried inside ``screening.json`` so that somebody holding only the output
    can check a number against its source without this repo beside them. A lead
    time is worth exactly what its citation is worth.
    """
    return {
        "label": entry.label,
        "lead_time_days": entry.days,
        "lead_time_days_low": entry.days_low,
        "lead_time_basis": entry.basis,
        "confirmed": entry.confirmed,
        "statutory": entry.statutory,
        "source": entry.source,
        "url": entry.url,
        "verified_on": str(entry.verified_on) if entry.verified_on else None,
        "not_found": entry.not_found,
    }


def citations(table, flag_types):
    """The citation for every flag type a run actually screened for."""
    wanted = set(flag_types)
    return {key: cite(entry) for key, entry in table.items() if key in wanted}
