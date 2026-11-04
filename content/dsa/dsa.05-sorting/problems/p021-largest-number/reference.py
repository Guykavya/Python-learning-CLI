from functools import cmp_to_key

n = int(input())
a = input().split()


def cmp(x, y):
    if x + y > y + x:
        return -1
    if x + y < y + x:
        return 1
    return 0


a.sort(key=cmp_to_key(cmp))
result = "".join(a)
print("0" if result[0] == "0" else result)
