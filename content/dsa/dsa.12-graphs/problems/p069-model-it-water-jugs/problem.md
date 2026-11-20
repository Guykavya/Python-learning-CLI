# Model it: the water jug puzzle

You have a 3-litre jug A and a 5-litre jug B, both empty, and a tap. A move is one of: fill A, fill B, empty A, empty B, pour A into B (until A is empty or B is full), pour B into A (until B is empty or A is full). Can you measure exactly 4 litres, and in how few moves?

Nothing here says "graph", but it is one (chapter section 18): a **vertex** is a state `(litres in A, litres in B)`, an **edge** is a move, and "fewest moves" is a shortest path in steps, so **BFS**. The program below does exactly that and prints, for every state it takes out of the queue, the states that are **new** (never seen before). Predict **exactly** what it prints. Do not run it.

```python
from collections import deque


def jugs(a_cap, b_cap, goal):
    start = (0, 0)
    parent = {start: None}
    queue = deque([start])
    while queue:
        a, b = queue.popleft()
        if a == goal or b == goal:
            path = []
            state = (a, b)
            while state is not None:
                path.append(state)
                state = parent[state]
            path.reverse()
            print(f"found ({a}, {b}) after {len(path) - 1} moves")
            return path
        pour_ab = min(a, b_cap - b)                  # how much A can pour into B
        pour_ba = min(b, a_cap - a)                  # how much B can pour into A
        moves = [(a_cap, b), (a, b_cap), (0, b), (a, 0),
                 (a - pour_ab, b + pour_ab), (a + pour_ba, b - pour_ba)]
        new = []
        for state in moves:
            if state not in parent:
                parent[state] = (a, b)
                queue.append(state)
                new.append(state)
        print(f"({a}, {b}) -> new {new}")
    return None


print(jugs(3, 5, 4))
```


Write your answer in `answer.txt`, one printed line per line (fifteen lines). A line `(a, b) -> new [...]` lists the new states in the order of the `moves` list; the last line is the returned path.

## How to work

1. For every state, write the six moves in the program's order: fill A, fill B, empty A, empty B, pour A into B, pour B into A. For the pours, `pour_ab = min(a, 5 - b)` and `pour_ba = min(b, 3 - a)`.
2. Keep a list of all states seen so far (the keys of `parent`) and the queue. A move that gives a state already seen produces nothing new; moves that change nothing (emptying an empty jug) give a seen state too.
3. The goal is checked when a state is **taken out** of the queue, not when it is found. So states can be printed after the goal state was first discovered.

## After you answer

1. Write the solution as instructions ("fill B, pour B into A, ..."). How much water is in each jug after every move?
2. How many different states did the search discover in total, including `(3, 1)`? Can every pair `(a, b)` with `0 <= a <= 3` and `0 <= b <= 5` be reached? Which states can be reached at all (look at what every reached state has in common)?
3. Why is BFS the right search here, and not DFS?
