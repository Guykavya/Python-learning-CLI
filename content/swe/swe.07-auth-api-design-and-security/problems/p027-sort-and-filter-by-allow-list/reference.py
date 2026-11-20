SORTS = {"created", "-created", "total"}
STATUSES = {"pending", "paid", "cancelled"}
PARAMS = {"sort", "status", "limit"}


class ListingError(Exception):
    """A bad query parameter. The API answers 400 with this message."""

    status = 400


def _allowed(values):
    return ", ".join(sorted(values))


def parse_listing(params: dict) -> dict:
    unknown = sorted(set(params) - PARAMS)
    if unknown:
        raise ListingError(f"unknown parameter {unknown[0]!r}; allowed parameters: {_allowed(PARAMS)}")
    sort = params.get("sort", "-created")
    if sort not in SORTS:
        raise ListingError(f"invalid sort {sort!r}; allowed sort values: {_allowed(SORTS)}")
    status = params.get("status")
    if status is not None and status not in STATUSES:
        raise ListingError(f"invalid status {status!r}; allowed status values: {_allowed(STATUSES)}")
    raw = params.get("limit", "20")
    if not (raw.isascii() and raw.isdigit()) or not 1 <= int(raw) <= 100:
        raise ListingError(f"invalid limit {raw!r}; limit must be a whole number from 1 to 100")
    return {"sort": sort, "status": status, "limit": int(raw)}
