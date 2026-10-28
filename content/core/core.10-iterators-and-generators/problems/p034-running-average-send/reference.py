from collections.abc import Generator


def averager() -> Generator[float | None, float | None, None]:
    total = 0.0
    count = 0
    average = None
    while True:
        received = yield average
        if received is None:
            total = 0.0
            count = 0
            average = None
        else:
            total += received
            count += 1
            average = total / count
