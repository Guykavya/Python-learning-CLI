n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]


def at_most(m):
    """Number of subarrays with at most m distinct values."""
    count = {}
    left = 0
    total = 0
    for right in range(len(a)):
        x = a[right]
        count[x] = count.get(x, 0) + 1
        while len(count) > m:
            y = a[left]
            count[y] -= 1
            if count[y] == 0:
                del count[y]
            left += 1
        total += right - left + 1
    return total


print(at_most(k) - at_most(k - 1))
