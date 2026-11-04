n = int(input())
a = [int(x) for x in input().split()]


def sort_count(a):
    if len(a) <= 1:
        return a, 0
    mid = len(a) // 2
    left, x = sort_count(a[:mid])
    right, y = sort_count(a[mid:])
    out = []
    i = j = 0
    cross = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
            cross += len(left) - i
    out.extend(left[i:])
    out.extend(right[j:])
    return out, x + y + cross


print(sort_count(a)[1])
