# Dungeon game

A knight starts in the top-left room of a grid `dungeon` and must reach the bottom-right room, moving only **right or down**. Entering a room changes his health by `dungeon[r][c]`: negative numbers are demons (damage), positive ones are potions. The first and the last room count too. If his health ever drops to **0 or below**, he dies. Write `min_initial_health(dungeon)` that returns the smallest starting health (at least 1) that lets him reach the end alive.

## Example

```python
>>> min_initial_health([[-2, -3, 3],
...                     [-5, -10, 1],
...                     [10, 30, -5]])     # right, right, down, down
7
>>> min_initial_health([[0]])              # he needs to be alive: 1
1
>>> min_initial_health([[100]])            # a potion does not lower the need below 1
1
>>> min_initial_health([[-5]])
6
```

With 7 on the path right, right, down, down: 7 → 5 → 2 → 5 → 6 → 1. Always above 0.

## Constraints

- `1 <= rows, cols <= 200`, values in `-1000 .. 1000`.
- This idea is not in the chapter; the hints teach it. A recursion without a memo is exponential.

## Think about

1. Try the forward direction: "the best health on arrival at `(r, c)`". The path with the most health at the end can dip very low in the middle. Why does one number per cell not decide the answer going forwards?
2. Now go **backwards**: `need[r][c]` = the smallest health you must have when you **enter** `(r, c)` to survive from there to the end. What is `need` in the last room? Then what is it in a room whose next step is a room needing `k`?
