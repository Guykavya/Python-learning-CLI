n = int(input())
a = [int(x) for x in input().split()]


def sift_down(a, i, size):
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        big = i
        if left < size and a[left] > a[big]:
            big = left
        if right < size and a[right] > a[big]:
            big = right
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big


for i in range(n // 2 - 1, -1, -1):
    sift_down(a, i, n)
for end in range(n - 1, 0, -1):
    a[0], a[end] = a[end], a[0]
    sift_down(a, 0, end)
print(" ".join(map(str, a)))
