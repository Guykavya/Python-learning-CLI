class PrefixSums:
    def __init__(self, a):
        self.a = list(a)
        self.n = len(a)
        self.pre = [0] * (self.n + 1)
        for i, x in enumerate(a):
            self.pre[i + 1] = self.pre[i] + x

    def query(self, l, r):
        return self.pre[r] - self.pre[l]

    def set(self, i, v):
        delta = v - self.a[i]
        self.a[i] = v
        pre = self.pre
        for k in range(i + 1, self.n + 1):      # every prefix longer than i contains a[i]
            pre[k] += delta
        return self.n - i
