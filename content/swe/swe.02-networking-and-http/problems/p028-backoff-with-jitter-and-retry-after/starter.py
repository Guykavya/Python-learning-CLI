from email.utils import parsedate_to_datetime


def delays(attempts, base, cap, rng):
    # TODO: one value per attempt: rng.uniform(0, min(cap, base * 2**i))
    return []


def retry_after(header, now, cap=None):
    # TODO: None, digits, or an HTTP date; never negative; capped
    return None
