n = int(input())
a = [int(x) for x in input().split()]

# a[0..low-1] are 0s, a[low..mid-1] are 1s, a[mid..high] unknown, a[high+1..n-1] are 2s.
low, mid, high = 0, 0, n - 1
while mid <= high:
    if a[mid] == 0:
        a[low], a[mid] = a[mid], a[low]
        low += 1
        mid += 1
    elif a[mid] == 1:
        mid += 1
    else:
        a[mid], a[high] = a[high], a[mid]
        high -= 1              # do NOT move mid: the value swapped in is still unknown

print(" ".join(map(str, a)))
