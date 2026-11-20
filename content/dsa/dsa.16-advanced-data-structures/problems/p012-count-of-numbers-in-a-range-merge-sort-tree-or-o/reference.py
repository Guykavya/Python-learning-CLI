class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total


def count_below(a, queries):
    n = len(a)
    order = sorted(range(n), key=lambda i: a[i])           # positions by mark
    bit = Fenwick(n)                                        # 1 at every inserted position
    answers = [0] * len(queries)
    j = 0
    for qi in sorted(range(len(queries)), key=lambda i: queries[i][2]):
        l, r, x = queries[qi]
        while j < n and a[order[j]] < x:                    # insert every mark < x
            bit.add(order[j], 1)
            j += 1
        answers[qi] = bit.prefix(r) - bit.prefix(l)
    return answers
