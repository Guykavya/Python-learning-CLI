BITS = 31


def max_xor(nums):
    root = {}

    def insert(x):
        node = root
        for b in range(BITS - 1, -1, -1):
            node = node.setdefault((x >> b) & 1, {})

    def best_partner(x):
        node, value = root, 0
        for b in range(BITS - 1, -1, -1):
            bit = (x >> b) & 1
            want = 1 - bit                     # the opposite bit gives a 1 in the XOR
            if want in node:
                value |= 1 << b
                node = node[want]
            else:
                node = node[bit]               # forced to match: this XOR bit is 0
        return value

    best = 0
    insert(nums[0])
    for x in nums[1:]:
        best = max(best, best_partner(x))
        insert(x)
    return best
