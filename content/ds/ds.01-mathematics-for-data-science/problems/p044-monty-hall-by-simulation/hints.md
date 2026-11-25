## Hint 1

If you switch, when do you win? Think about what your first pick was: car or goat. The host removes a goat, so the other closed door is...

## Hint 2

```text
car, pick = random doors
if pick == car: host opens one of the other two; switching loses
else: host opens the only other goat; switching goes to the car
```
Implement the host honestly (a loop is fine for 20,000 trials).
