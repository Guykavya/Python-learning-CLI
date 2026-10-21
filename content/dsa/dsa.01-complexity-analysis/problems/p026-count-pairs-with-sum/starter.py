n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

# Plan:
# 1. Constraints: n up to 200000. Which complexity do I need?
# 2. Standing at position j, which earlier values pair with a[j]? How many of them are there?
# 3. What do I need to remember about the earlier positions to answer that in O(1)?
# 4. Check with "4 4 / 2 2 2 2" (answer 6) and "4 0 / -1 1 -1 1" (answer 4).
