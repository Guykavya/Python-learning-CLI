from collections.abc import Generator


def averager() -> Generator[float | None, float | None, None]:
    # Keep a total and a count in local variables.
    # Use  received = yield current_average  inside a loop.
    yield None
