# This program is correct but far too slow on large logs. Find the slow parts and fix them.
n = int(input())
queue = [int(x) for x in input().split()]

seen = []
served = 0
repeat_visits = 0
while len(queue) > 0:
    user = queue.pop(0)
    if user in seen:
        repeat_visits += 1
    else:
        seen.append(user)
    served += 1

print("served", served)
print("new users", len(seen))
print("repeat visits", repeat_visits)
