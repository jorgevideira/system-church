"""Date utility functions."""

import calendar
from datetime import date, datetime, timezone
from typing import Optional


_DEFAULT_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%Y%m%d",
    "%d.%m.%Y",
]


def get_current_utc() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def format_date(d: date, fmt: str = "%Y-%m-%d") -> str:
    """Format *d* using *fmt*."""
    return d.strftime(fmt)


def parse_date(date_str: str, formats: Optional[list[str]] = None) -> Optional[date]:
    """Try to parse *date_str* with each format in *formats*.

    Returns a ``date`` object on success, or ``None`` if no format matched.
    """
    if not date_str:
        return None
    for fmt in (formats or _DEFAULT_FORMATS):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def get_month_range(year: int, month: int) -> tuple[date, date]:
    """Return (first_day, last_day) of the given month."""
    first = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    last = date(year, month, last_day)
    return first, last


def get_year_range(year: int) -> tuple[date, date]:
    """Return (Jan 1, Dec 31) of the given year."""
    return date(year, 1, 1), date(year, 12, 31)
