n = int(input())
rows = []
for _ in range(n):
    name, age, score = input().split()
    rows.append((name, int(age), int(score)))
k = int(input())
rules = []
INDEX = {"name": 0, "age": 1, "score": 2}
for _ in range(k):
    field, direction = input().split()
    rules.append((INDEX[field], direction == "asc"))


def goes_first(x, y):
    for idx, ascending in rules:
        if x[idx] != y[idx]:
            return (x[idx] < y[idx]) == ascending
    return True


def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if goes_first(left[i], right[j]):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


for name, age, score in merge_sort(rows):
    print(name, age, score)
