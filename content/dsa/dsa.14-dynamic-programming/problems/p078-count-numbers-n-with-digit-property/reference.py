import functools


def count_stepping(lo, hi):
    def upto(N):
        """Stepping numbers in [0, N]."""
        digits = list(map(int, str(N)))

        @functools.cache
        def go(pos, prev, tight, started):
            if pos == len(digits):
                return 1                       # one finished number (the number 0 if never started)
            limit = digits[pos] if tight else 9
            total = 0
            for d in range(limit + 1):
                now_tight = tight and d == limit
                if not started:
                    if d == 0:
                        total += go(pos + 1, -1, now_tight, False)   # still a leading zero
                    else:
                        total += go(pos + 1, d, now_tight, True)     # first real digit: anything goes
                elif abs(d - prev) == 1:
                    total += go(pos + 1, d, now_tight, True)
            return total

        return go(0, -1, True, False)

    return upto(hi) - (upto(lo - 1) if lo > 0 else 0)
