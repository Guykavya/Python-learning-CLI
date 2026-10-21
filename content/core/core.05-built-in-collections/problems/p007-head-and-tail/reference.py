nums = [int(x) for x in input().split()]
first, *middle, last = nums
print("First:", first)
print("Last:", last)
print("Middle:", " ".join(str(n) for n in middle) if middle else "(none)")
print("Middle sum:", sum(middle))
