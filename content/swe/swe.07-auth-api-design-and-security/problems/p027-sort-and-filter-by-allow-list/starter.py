SORTS = {"created", "-created", "total"}
STATUSES = {"pending", "paid", "cancelled"}
PARAMS = {"sort", "status", "limit"}


class ListingError(Exception):
    """A bad query parameter. The API answers 400 with this message."""

    status = 400


def parse_listing(params: dict) -> dict:
    raise NotImplementedError("write parse_listing()")
