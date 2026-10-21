n = int(input())
queue = [int(x) for x in input().split()]

seen = set()                 # was a list: `in` scanned it every time
served = 0
repeat_visits = 0
for user in queue:           # was queue.pop(0), which shifts every remaining item
    if user in seen:
        repeat_visits += 1
    else:
        seen.add(user)
    served += 1

print("served", served)
print("new users", len(seen))
print("repeat visits", repeat_visits)
