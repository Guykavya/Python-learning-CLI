n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

first_pos = {}          # value -> first position (0-based) where it appeared
answer = "none"
for j in range(n):
    need = t - a[j]
    if need in first_pos:
        answer = f"{first_pos[need] + 1} {j + 1}"
        break
    if a[j] not in first_pos:
        first_pos[a[j]] = j
print(answer)
