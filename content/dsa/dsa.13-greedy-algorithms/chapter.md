# dsa.13 Greedy algorithms

## 1. "Take the best thing you can see, and never look back"

You are at a till and must pay 87 rupees using as few notes and coins as possible. You do not think hard. You take the biggest note that is not too big (50), then the biggest that still fits in what is left (20), then 10, then 5, then 2. Nobody ever taught you a theorem for this. It just works.

```python
def make_change(amount, coins):
    """Always take the biggest coin that still fits."""
    used = []
    for c in sorted(coins, reverse=True):
        while amount >= c:
            amount -= c
            used.append(c)
    return used

print(make_change(87, [1, 2, 5, 10, 20, 50, 100]))
```
```text
[50, 20, 10, 5, 2]
```

That is a **greedy algorithm**: build the answer one step at a time, and at each step take the choice that looks best **right now**, without planning ahead and without ever undoing a choice.

Greedy algorithms are attractive for three reasons.

1. **They are short.** Most are a sort plus one loop.
2. **They are fast.** The cost is usually the sort, `O(n log n)`, or a heap, `O(n log n)`.
3. **They need almost no memory** beyond the input.

But there is a catch, and the whole chapter is about it. Run the same code on a slightly different money system.

```python
print(make_change(6, [1, 3, 4]))
print("best possible: [3, 3]")
```
```text
[4, 1, 1]
best possible: [3, 3]
```

The greedy rule took 4 first (the biggest that fits), then was forced to use two 1s. Three coins. But `3 + 3` needs only two. The greedy choice "take 4" **looked best and was wrong**, and the algorithm has no way to take it back.

So a greedy algorithm is not a trick that always works. It is a **bet** that "locally best" equals "globally best". For some problems the bet is a theorem. For others it is a trap. The skill this module teaches is the one skill that matters:

> **Decide whether the greedy choice is safe, and prove it, or find a counterexample.**

### What you can do after this module

1. **State the greedy pattern**: a choice rule, a commit, and a smaller problem left over.
2. **Prove a greedy choice is safe** with an **exchange argument** or a **stay-ahead argument**.
3. **Break a wrong greedy rule** by finding a small counterexample, and by testing it against brute force.
4. **Solve interval problems**: activity selection, merging intervals, minimum arrows, minimum platforms and meeting rooms.
5. **Solve scheduling problems**: shortest job first, deadlines with profits, minimising lateness.
6. **Solve array greedy problems**: jump game, gas station, assign cookies, buy and sell stock.
7. **Use fractional knapsack** and explain exactly why 0/1 knapsack breaks it.
8. **Decide when coin change is greedy-safe**, and when it needs dynamic programming.
9. **Build Huffman codes** with `heapq`, including the tie-breaker trap.
10. **Recognise greedy in algorithms you already know**: Kruskal, Prim and Dijkstra.

### What this module reuses

You already know the tools. This chapter does not re-teach them.

- **Sorting with `key`, stability and interval sweeps** are in dsa.05 (sorting), sections 2 and 16.
- **`heapq`, tuples as priorities and the tie-breaker trap** are in dsa.11 (heaps), sections 5 and 10.
- **Kruskal, Prim and Dijkstra**, all greedy, are in dsa.12 (graphs), sections 10 and 15.

If any of these feels shaky, glance back before you continue.

## 2. The shape of a greedy algorithm

Almost every greedy solution has the same three parts.

1. **A rule that ranks the candidates.** "Biggest coin", "earliest finish time", "highest profit", "lowest frequency". This rule is usually a sort key or a heap priority.
2. **A commitment.** Once a candidate is taken (or skipped) we never revisit it. No backtracking, no table of earlier answers.
3. **A smaller problem.** After the commitment, what is left is the same kind of problem, only smaller, and we repeat.

The code almost always looks like one of two templates.

```python
# Template A: sort once, then sweep
def greedy_sweep(items):
    items = sorted(items, key=ranking_rule)
    chosen = []
    for item in items:
        if fits(item, chosen):      # is it still allowed?
            chosen.append(item)     # commit
    return chosen

# Template B: a heap gives "the best remaining" again and again
import heapq
def greedy_heap(items):
    heap = build_heap(items)
    while heap:
        best = heapq.heappop(heap)
        use(best)                   # commit
        # maybe push new candidates that this step created
```

Template A is the topic of most of this chapter (interval scheduling, fractional knapsack, deadlines). Template B appeared in dsa.11 (connect the sticks, meeting rooms) and returns here for Huffman coding and for scheduling with deadlines.

### Greedy versus the other approaches

You now know three ways to attack an optimisation problem.

| Approach | Idea | Cost | Always correct? |
|---|---|---|---|
| **Brute force** | Try every combination | exponential, `O(2^n)` or `O(n!)` | yes |
| **Dynamic programming** (later module) | Try all choices, but reuse answers to repeated subproblems | polynomial, often `O(n * W)` | yes, when the problem has the right structure |
| **Greedy** | Pick one choice by a rule and never look back | usually `O(n log n)` | **only when you can prove it** |

Greedy is the cheapest and the riskiest. Dynamic programming is the safety net when the greedy bet fails. A good habit: **find a greedy idea, try to break it with small cases, and fall back to brute force or DP if you cannot prove it.**

### A first example that works: pick the biggest

You may take at most `k` items from a pile of numbers. Which `k` items give the biggest sum?

```python
def best_sum(values, k):
    return sum(sorted(values, reverse=True)[:k])

print(best_sum([4, 9, 1, 7, 3], 2))
```
```text
16
```

Why is this safe? Suppose the best choice did **not** include the biggest number `9`, and instead used some smaller number `x`. Swap `x` for `9`: the total does not go down, because `9 >= x`. So there is always a best answer that contains `9`. Take it, and the rest of the problem is "choose `k - 1` items from the remaining numbers", the same problem, smaller. That tiny argument is already an **exchange argument**, and it is the most important idea of the chapter. Section 3 names it and sharpens it.

## 3. When is a greedy choice safe?

A greedy algorithm is correct when two properties hold.

1. **Greedy-choice property.** There is always an optimal answer that **contains** the greedy choice. (You may need to rearrange an optimal answer to see this, but it exists.)
2. **Optimal substructure.** After making the greedy choice, the rest of an optimal answer is an optimal answer to the **smaller problem** that remains.

If both hold, induction finishes the proof: the first step is safe, the remaining problem is the same kind of problem, so the next step is safe too, and so on until nothing is left.

Property 2 is usually easy. Property 1 is the hard one, and there are two standard ways to prove it.

### Tool 1: the exchange argument

Take **any** optimal answer `O`. Suppose it does not contain the greedy choice `g`. Show that you can **exchange** something in `O` for `g` and get an answer `O'` that is **not worse**. Then `O'` is also optimal and contains `g`. So "an optimal answer containing `g`" exists.

The template for the argument:

1. Let `O` be an optimal answer that differs from the greedy answer `G`.
2. Find the **first place** where `O` and `G` differ.
3. Swap `O`'s choice there for `G`'s choice.
4. Show the result is still valid (nothing breaks) and no worse.
5. Repeat. Each swap makes `O` look more like `G`. After finitely many swaps `O` becomes `G`, so `G` is optimal.

A tiny exchange for the "pick the biggest" example in section 2 shows the idea in full: if the best answer skips the biggest number, swap one of its numbers for the biggest and the total cannot fall. For money the exchange is harder, because swapping one coin for another changes the amount paid. That is exactly why coin change is greedy-safe for some money systems and not others (section 9).

### Tool 2: the stay-ahead argument

Sometimes the greedy answer is built step by step and you can compare it with an optimal answer **after each step**. Show that after step `i`, greedy is **at least as good as** the optimal answer on some measure ("has used less time", "has reached further"). If greedy "stays ahead" at every step, it cannot finish behind.

Template:

1. Pick a measure `m` that is easy to compare. For example, "the finish time of the `i`-th chosen activity".
2. Prove, by induction, that after `i` steps greedy's `m` is as good as the optimal answer's `m`.
3. Conclude that greedy finishes at least as well.

Exchange arguments change the optimal answer into the greedy one. Stay-ahead arguments compare them side by side. Both reach the same destination, and often both work on the same problem. Choose the one whose picture you find easier.

### The cheap alternative: try to break it

A proof is best, but you do not always have time. A **counterexample** is the other half of the skill, and it is far cheaper. To break a greedy rule:

1. Try **tiny inputs** with 3 or 4 items, by hand, where the rule's choice and the true best differ.
2. Look at **ties**, **extreme values**, and **one huge item** among small ones. Greedy rules most often break when a single item is "tempting but wrong".
3. **Compare with a brute-force solution** on thousands of random small inputs. Section 15 builds exactly this harness.

If a rule survives 10,000 random small cases, it may still be wrong, but your confidence is far higher. If it fails once, you have the counterexample and you are done.

### The rule of three questions

Before coding any greedy solution, ask:

1. **What is the choice?** (What am I picking at each step?)
2. **Why is the best-looking choice safe?** (Exchange or stay-ahead, in one sentence.)
3. **After I commit, is what remains the same problem?** (If the remaining problem changes shape, greedy may fail.)

If you cannot answer question 2 in one honest sentence, treat the algorithm as unproven until you have tested it.

### Predict the output 1

What does this print?

```python
def make_change(amount, coins):
    used = []
    for c in sorted(coins, reverse=True):
        while amount >= c:
            amount -= c
            used.append(c)
    return used

print(len(make_change(30, [1, 10, 25])))
print(len(make_change(40, [1, 10, 25, 50])))
```
<details><summary>Answer</summary>

```text
6
7
```

For 30, greedy takes 25 and then five 1s: six coins. But three 10s would be only three coins. This system (1, 10, 25) is not greedy-safe. For 40, greedy takes 25, then a 10, then five 1s: seven coins, while four 10s would use only four coins. Section 9 shows exactly when a coin system is safe.

</details>

## 4. Activity selection: the classic greedy

### The problem

A hall can host one event at a time. You are given requests, each with a start time and an end time. Choose the **largest number** of events so that no two overlap.

We treat each event as a **half-open** interval `[start, end)`: an event that ends at 5 and one that starts at 5 do **not** overlap (the hall is free at 5). This is the usual convention. Section 5 shows what changes when touching counts as overlapping.

```python
events = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
print(len(events), "requests")
```
```text
11 requests
```

Which event do we commit to first? There are many plausible rules. Let us test the four most natural ones before we trust any.

### Four tempting rules

1. **Earliest start first.** "Start using the hall as soon as possible."
2. **Shortest first.** "Short events leave more room."
3. **Fewest conflicts first.** "Pick the event that blocks the least."
4. **Earliest finish first.** "Free the hall as soon as possible."

Three of them are wrong. Here are the counterexamples, found by thinking about "one tempting but wrong choice".

```python
def pick(events, key):
    """Greedy: sort by key, take an event if it does not overlap the last taken one."""
    chosen = []
    last_end = float("-inf")
    for s, e in sorted(events, key=key):
        if s >= last_end:
            chosen.append((s, e))
            last_end = e
    return chosen

# Rule 1 fails: one very long event that starts first
a = [(0, 10), (1, 2), (3, 4), (5, 6)]
print("earliest start:", pick(a, key=lambda ev: ev[0]))
print("best answer   :", [(1, 2), (3, 4), (5, 6)])

# Rule 2 fails: the shortest event sits across two others
b = [(0, 5), (4, 7), (6, 10)]
print("shortest first:", pick(b, key=lambda ev: ev[1] - ev[0]))
print("best answer   :", [(0, 5), (6, 10)])
```
```text
earliest start: [(0, 10)]
best answer   : [(1, 2), (3, 4), (5, 6)]
shortest first: [(4, 7)]
best answer   : [(0, 5), (6, 10)]
```

In the first case the earliest-starting event is huge and blocks everyone. In the second the shortest event, `(4, 7)`, overlaps both others even though each of those two fits with nothing else in the way.

Rule 3 ("fewest conflicts") is more subtle. It is also wrong, but you need ten intervals to see it. Here is one such input (found by a random search against brute force, the technique of section 15).

```python
def brute_best(events):
    """Largest set of non-overlapping events, trying every subset (small inputs only)."""
    best = 0
    for mask in range(1 << len(events)):
        chosen = sorted(events[i] for i in range(len(events)) if mask >> i & 1)
        if all(chosen[i][1] <= chosen[i + 1][0] for i in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return best

def fewest_conflicts(events):
    left = list(events)
    count = 0
    while left:
        def conflicts(x):
            return sum(1 for y in left if y is not x and y[0] < x[1] and x[0] < y[1])
        x = min(left, key=conflicts)
        count += 1
        left = [y for y in left if not (y[0] < x[1] and x[0] < y[1])]
    return count

c = [(5, 9), (9, 12), (11, 15), (10, 13), (8, 10), (0, 3), (4, 8), (2, 5), (1, 5), (10, 11)]
print("fewest conflicts picks", fewest_conflicts(c), "events; the true best is", brute_best(c))
```
```text
fewest conflicts picks 4 events; the true best is 5
```

Lesson: **an obvious-sounding rule can fail on an input you would never draw by hand.** This is why testing against brute force is a normal part of designing greedy algorithms.

### The winner: earliest finish time

Rule 4 is correct. Sort by **end time**, take the first event, then repeatedly take the next event whose start is at or after the end of the last one you took.

```python
def select_activities(events):
    chosen = []
    last_end = float("-inf")
    for s, e in sorted(events, key=lambda ev: (ev[1], ev[0])):
        if s >= last_end:        # fits after the last chosen event
            chosen.append((s, e))
            last_end = e
    return chosen

print(select_activities(events))
print("brute force agrees:", brute_best(events[:10]) , "on the first 10 requests")
print("greedy on those 10:", len(select_activities(events[:10])))
```
```text
[(1, 4), (5, 7), (8, 11), (12, 16)]
brute force agrees: 3 on the first 10 requests
greedy on those 10: 3
```

The brute force ran only on the first ten requests (it tries every subset, which is `2^n`). It agrees with greedy on that smaller input.

Why sort by `(end, start)` and not only by `end`? Two events with the same end time can be taken in either order for the count, but a deterministic key makes the output the same every run, and it helps tests.

### Hand trace

Sorted by end, the eleven events are listed below. We keep `last_end` and decide for each.

```python
last_end = float("-inf")
for s, e in sorted(events, key=lambda ev: (ev[1], ev[0])):
    if s >= last_end:
        print(f"({s:2},{e:2})  start {s:2} >= last_end {last_end} -> TAKE")
        last_end = e
    else:
        print(f"({s:2},{e:2})  start {s:2} <  last_end {last_end} -> skip")
```
```text
( 1, 4)  start  1 >= last_end -inf -> TAKE
( 3, 5)  start  3 <  last_end 4 -> skip
( 0, 6)  start  0 <  last_end 4 -> skip
( 5, 7)  start  5 >= last_end 4 -> TAKE
( 3, 9)  start  3 <  last_end 7 -> skip
( 5, 9)  start  5 <  last_end 7 -> skip
( 6,10)  start  6 <  last_end 7 -> skip
( 8,11)  start  8 >= last_end 7 -> TAKE
( 8,12)  start  8 <  last_end 11 -> skip
( 2,14)  start  2 <  last_end 11 -> skip
(12,16)  start 12 >= last_end 11 -> TAKE
```

Read the trace as a story. We take `(1, 4)` because it finishes first. Then everything that starts before 4 is skipped (`(3, 5)`, `(0, 6)` and so on). `(5, 7)` is the first event starting at or after 4, so we take it, and so on. We never go back.

### Why earliest finish is safe: the exchange argument

Let `g` be the event that finishes first. Take **any** optimal schedule `O`, sorted by end time, and let `f` be its first event.

- `g` finishes no later than `f`, because `g` finishes first of all events.
- So `g` cannot collide with the second event of `O`: that event starts after `f` ends, and `f` ends after `g` ends (or at the same time).
- Replace `f` with `g`. The schedule is still valid (no overlaps) and has the same size.

So there is an optimal schedule that contains `g`. After taking `g`, the remaining problem is "choose the most events that start at or after `g`'s end", the same problem on a subset of the events. Induction finishes the proof.

### Why it is safe: the stay-ahead argument

Another angle. Let greedy pick events `g1, g2, ..., gk` and an optimal schedule pick `o1, o2, ..., om`, both in order. **Claim: `end(gi) <= end(oi)` for every `i`.**

- For `i = 1` it is true because `g1` is the event with the earliest end.
- Suppose `end(g_i) <= end(o_i)`. The event `o_{i+1}` starts after `o_i` ends, so after `g_i` ends too. So `o_{i+1}` was available when greedy chose `g_{i+1}`, and greedy chose the earliest-ending available one: `end(g_{i+1}) <= end(o_{i+1})`.

Greedy always "stays ahead": it frees the hall no later than the optimal schedule. If the optimal schedule has `m` events but greedy stopped at `k < m`, then `o_{k+1}` would start after `end(o_k) >= end(g_k)` and greedy would have taken it. Contradiction. So `k >= m`, and greedy is optimal.

### Complexity

- Sorting dominates: `O(n log n)`.
- The sweep is `O(n)`.
- Extra space `O(n)` for the sorted copy and the answer.

If the events are already sorted by end time, the algorithm is `O(n)`.

### Predict the output 2

```python
ev = [(0, 3), (2, 4), (3, 6), (5, 7), (6, 9)]
print(select_activities(ev))
```
<details><summary>Answer</summary>

```text
[(0, 3), (3, 6), (6, 9)]
```

Sorted by end: `(0,3)`, `(2,4)`, `(3,6)`, `(5,7)`, `(6,9)`. Take `(0,3)`. `(2,4)` starts at 2 < 3: skip. `(3,6)` starts at 3 >= 3: take (touching is allowed). `(5,7)` starts at 5 < 6: skip. `(6,9)` starts at 6 >= 6: take.

</details>

## 5. Variants of interval scheduling

Once you know the earliest-finish sweep, a family of problems turns out to be the same problem in disguise.

### Return which requests (not only how many)

If each request has an id, keep the id with the interval. Sort the *indices*, not the values, so you can report the original positions.

```python
def select_ids(events):
    order = sorted(range(len(events)), key=lambda i: (events[i][1], events[i][0]))
    chosen = []
    last_end = float("-inf")
    for i in order:
        s, e = events[i]
        if s >= last_end:
            chosen.append(i)
            last_end = e
    return chosen

meetings = [(9, 10), (9, 12), (11, 13), (10, 11), (12, 14)]
print(select_ids(meetings))
```
```text
[0, 3, 2]
```

The output is a list of **original positions**, in the order they were picked. Positions 0, 3 and 2 are `(9, 10)`, `(10, 11)` and `(11, 13)`. Let us print the intervals to be sure.

```python
print([meetings[i] for i in select_ids(meetings)])
```
```text
[(9, 10), (10, 11), (11, 13)]
```

Three meetings, none overlapping: 9 to 10, 10 to 11 and 11 to 13. The meeting `(12, 14)` overlaps `(11, 13)`, so it is skipped.

### Non-overlapping intervals: the minimum number to remove

"Given intervals, what is the fewest to remove so the rest do not overlap?" Keeping the **most** intervals is exactly activity selection, so:

```text
removals = n - (largest non-overlapping set)
```

```python
def min_removals(intervals):
    return len(intervals) - len(select_activities(intervals))

print(min_removals([(1, 2), (2, 3), (3, 4), (1, 3)]))
print(min_removals([(1, 2), (1, 2), (1, 2)]))
print(min_removals([(1, 2), (2, 3)]))
```
```text
1
2
0
```

In the first case `(1, 3)` overlaps two others, so removing it leaves `(1,2),(2,3),(3,4)`: one removal. In the second, three copies of the same interval: keep one, remove two. In the third, touching intervals are fine.

A common alternative way to say the same thing: when two intervals overlap, **remove the one that ends later**, because it blocks more of the future. That is the same exchange argument, written as a loop that keeps `prev_end`.

### Minimum arrows to burst balloons

Balloons are drawn as horizontal segments `[x_start, x_end]`. An arrow shot straight up at position `x` bursts every balloon with `x_start <= x <= x_end`. Find the fewest arrows.

Here the intervals are **closed**: balloons that touch at one point can be burst together. The greedy idea: sort by end, shoot at the end of the first balloon (the furthest right you can shoot and still hit it), and skip every balloon that this arrow also hits.

```python
def min_arrows(balloons):
    arrows = 0
    shot_at = float("-inf")
    for s, e in sorted(balloons, key=lambda b: b[1]):
        if s > shot_at:          # strictly greater: touching is still hit
            arrows += 1
            shot_at = e
    return arrows

print(min_arrows([(10, 16), (2, 8), (1, 6), (7, 12)]))
print(min_arrows([(1, 2), (3, 4), (5, 6), (7, 8)]))
print(min_arrows([(1, 2), (2, 3), (3, 4), (4, 5)]))
```
```text
2
4
2
```

Trace the first input. Sorted by end: `(1,6)`, `(2,8)`, `(7,12)`, `(10,16)`. Shoot at 6: it bursts `(1,6)` and `(2,8)` (2 <= 6). `(7,12)` starts at 7 > 6: new arrow at 12. `(10,16)` starts at 10 <= 12, already burst. Two arrows. In the last input each arrow can hit two touching balloons: arrows at 2 and 4.

Compare the two conditions carefully, because this is a favourite exam trap:

| Problem | Touching intervals | Condition to start a new group |
|---|---|---|
| Activity selection (half-open) | do **not** overlap | take when `s >= last_end` |
| Balloons (closed) | **do** overlap | new arrow when `s > shot_at` |

### Weighted intervals: where earliest finish breaks

Now give each event a **value** and maximise the total value, not the count.

```python
weighted = [(0, 10, 100), (1, 3, 1), (4, 6, 1), (7, 9, 1)]   # (start, end, value)

def greedy_by_end_weighted(items):
    total = 0
    last_end = float("-inf")
    for s, e, v in sorted(items, key=lambda x: x[1]):
        if s >= last_end:
            total += v
            last_end = e
    return total

print("earliest finish takes value", greedy_by_end_weighted(weighted))
print("taking only the big event gives", 100)
```
```text
earliest finish takes value 3
taking only the big event gives 100
```

Earliest finish grabs three small events worth 3 and misses the big one worth 100. No simple sort key repairs this; **weighted interval scheduling needs dynamic programming** (a later module). The lesson: greedy depends on the objective. The same intervals with "maximise the count" are greedy-safe; with "maximise the value" they are not.

## 6. Merging intervals, meeting rooms and platforms

These problems start with sorting, as in dsa.05 section 16. We revisit them from the greedy point of view, and add the harder question "how many resources do we need at once?".

### Merge overlapping intervals

Sort by **start**. Keep the current merged interval. For each next interval, either it starts inside the current one (extend its end) or it starts after (close the current one and begin a new one).

```python
def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:             # overlaps (touching counts here)
            out[-1][1] = max(out[-1][1], e)     # extend; max matters!
        else:
            out.append([s, e])
    return out

print(merge([(1, 3), (2, 6), (8, 10), (15, 18)]))
print(merge([(1, 4), (4, 5)]))
print(merge([(1, 10), (2, 3), (4, 5)]))
```
```text
[[1, 6], [8, 10], [15, 18]]
[[1, 5]]
[[1, 10]]
```

The third call is the reason for `max`: `(2, 3)` is inside `(1, 10)` and must not *shrink* the end to 3. Why does sorting by start make greedy safe? After sorting, an interval that does not overlap the current merged block cannot overlap any *earlier* block either, because every earlier block ends before the current block began. So once we close a block, it is final.

Complexity: `O(n log n)` for the sort, `O(n)` for the sweep.

### Meeting rooms I: can one person attend all?

Sort by start; if any meeting starts before the previous one ends, the answer is no.

```python
def can_attend_all(meetings):
    ordered = sorted(meetings)
    return all(ordered[i][1] <= ordered[i + 1][0] for i in range(len(ordered) - 1))

print(can_attend_all([(0, 30), (5, 10), (15, 20)]))
print(can_attend_all([(7, 10), (2, 4)]))
```
```text
False
True
```

### Minimum platforms (meeting rooms II) by two pointers

A station has trains with arrival and departure times. What is the minimum number of platforms so that no train waits? This is the same as "meeting rooms II" and as "what is the largest number of intervals that overlap at one moment?".

The idea: forget which arrival belongs to which departure. Sort **all arrivals** and **all departures** separately, then walk through time. Each arrival adds a train on a platform; each departure removes one. The highest count seen is the answer.

When a train arrives at the exact minute another leaves, may they share a platform? Here we decide: the leaving train is gone first (departure at `t` frees the platform for an arrival at `t`). Many textbook versions decide the other way, so read the statement.

```python
def min_platforms(arrivals, departures):
    arr = sorted(arrivals)
    dep = sorted(departures)
    i = j = 0
    on_platform = best = 0
    while i < len(arr):
        if arr[i] < dep[j]:        # next event is an arrival
            on_platform += 1
            best = max(best, on_platform)
            i += 1
        else:                      # a departure (also when equal times)
            on_platform -= 1
            j += 1
    return best

arrivals   = [900, 940, 950, 1100, 1500, 1800]
departures = [910, 1200, 1120, 1130, 1900, 2000]
print(min_platforms(arrivals, departures))
```
```text
3
```

Hand trace. Sorted arrivals: `900, 940, 950, 1100, 1500, 1800`. Sorted departures: `910, 1120, 1130, 1200, 1900, 2000`.

```python
arr = sorted(arrivals)
dep = sorted(departures)
i = j = 0
on_platform = best = 0
while i < len(arr):
    if arr[i] < dep[j]:
        on_platform += 1
        best = max(best, on_platform)
        print(f"time {arr[i]:4}: arrival   -> {on_platform} on platforms")
        i += 1
    else:
        on_platform -= 1
        print(f"time {dep[j]:4}: departure -> {on_platform} on platforms")
        j += 1
print("most at once:", best)
```
```text
time  900: arrival   -> 1 on platforms
time  910: departure -> 0 on platforms
time  940: arrival   -> 1 on platforms
time  950: arrival   -> 2 on platforms
time 1100: arrival   -> 3 on platforms
time 1120: departure -> 2 on platforms
time 1130: departure -> 1 on platforms
time 1200: departure -> 0 on platforms
time 1500: arrival   -> 1 on platforms
time 1800: arrival   -> 2 on platforms
most at once: 3
```

The peak is 3, reached at time 1100: the trains that arrived at 940 and 950 have not left yet (the earliest remaining departure is 1120), and now a third train arrives. The loop stops when every arrival has been processed, because the remaining departures can only lower the count.

Complexity: two sorts, `O(n log n)`, and a linear merge-like walk. Space `O(n)`.

Why is this a "greedy" algorithm? We do not assign each train to a named platform. We only ask *how many* are needed at the busiest moment. Section "interval partitioning" below shows that this number is also enough.

### The same answer with a heap

If you prefer to think of rooms, sort the meetings by start and keep a **min-heap of end times**, one for each room in use. For each new meeting: if the room that frees up soonest (`heap[0]`) is free by the time this meeting starts, reuse it (pop); then push this meeting's end.

```python
import heapq

def min_rooms(meetings):
    ends = []                                 # min-heap of end times of rooms in use
    for s, e in sorted(meetings):
        if ends and ends[0] <= s:
            heapq.heappop(ends)               # reuse the room that frees first
        heapq.heappush(ends, e)
    return len(ends)

print(min_rooms([(0, 30), (5, 10), (15, 20)]))
print(min_rooms([(7, 10), (2, 4)]))
print(min_rooms([(1, 5), (2, 6), (3, 7), (4, 8)]))
```
```text
2
1
4
```

The heap size is the number of rooms in use right now, and the final size is the maximum ever needed, since a room is only freed when a new meeting takes it. This was one of the greedy-with-a-heap examples in dsa.11 section 10. Complexity: `O(n log n)` time and `O(n)` space.

### Interval partitioning: why the count is exactly the maximum depth

The **depth** at a moment is how many intervals cover it. Clearly you need at least `max depth` rooms, because at the busiest moment that many meetings run together. The two algorithms above show you need **no more** than the max depth: they place every meeting in some room and never open a new room unless every existing room is busy at that moment. So:

> minimum rooms = maximum number of meetings that overlap at any single moment.

This "lower bound meets upper bound" argument is a third way to prove a greedy algorithm: show a lower bound for *every* algorithm, and show that greedy reaches it.

### Predict the output 3

```python
print(min_rooms([(1, 3), (3, 5), (5, 7)]))
print(min_rooms([(1, 4), (2, 5), (3, 6), (7, 8)]))
```
<details><summary>Answer</summary>

```text
1
3
```

The first list touches end to start, so one room is reused three times. In the second list the first three meetings overlap at time 3 (all running), so three rooms; the fourth meeting `(7, 8)` reuses one.

</details>

## 7. Fractional knapsack

### The problem

A thief has a bag that holds at most `W` kilograms. In front of them are items; item `i` has a weight `w_i` and a value `v_i`. The thief may take **any fraction** of an item: half a bag of gold dust is worth half as much and weighs half as much. Maximise the total value.

Which item first? The weights and values both matter, so neither is the right key by itself. The thing that matters is **value per kilogram**, the item's *density*. Every kilogram of a dense item is worth more than every kilogram of a thin one, so we fill the bag with the densest item first, then the next, and so on. The last item may be taken only partly.

```python
def fractional_knapsack(items, capacity):
    """items: list of (value, weight). Returns (best value, how much of each item was taken)."""
    order = sorted(range(len(items)), key=lambda i: items[i][0] / items[i][1], reverse=True)
    total = 0.0
    taken = [0.0] * len(items)
    room = capacity
    for i in order:
        value, weight = items[i]
        if room <= 0:
            break
        part = min(weight, room)          # the whole item, or whatever still fits
        taken[i] = part / weight          # fraction of the item taken
        total += value * part / weight
        room -= part
    return total, taken

items = [(60, 10), (100, 20), (120, 30)]       # (value, weight)
print([round(v / w, 2) for v, w in items], "<- value per kilogram")
print(fractional_knapsack(items, 50))
```
```text
[6.0, 5.0, 4.0] <- value per kilogram
(240.0, [1.0, 1.0, 0.6666666666666666])
```

### Hand trace

Densities: item 0 is `60/10 = 6`, item 1 is `100/20 = 5`, item 2 is `120/30 = 4`. The order is 0, 1, 2. Capacity 50.

1. Take all of item 0: weight 10, value 60. Room left: 40.
2. Take all of item 1: weight 20, value 100. Room left: 20.
3. Item 2 weighs 30 but only 20 fits: take `20/30 = 2/3` of it, worth `120 * 2/3 = 80`. Room left: 0.

Total: `60 + 100 + 80 = 240`, and the fractions printed are `1.0, 1.0, 0.666...`.

### Why it is correct

Exchange argument. Let item `a` be the densest. Suppose an optimal bag contains less of `a` than it could (it did not take all of `a`, and it has some other item `b` of lower density in the bag). Remove a little weight `d` of `b` and add `d` of `a`. The weight is unchanged. The value changes by `d * (density(a) - density(b)) >= 0`. So the bag is no worse. Keep exchanging until the densest item is used as much as possible, then repeat for the next densest. The fraction is what makes the exchange legal: we may remove *any amount* of `b`. In section 8 you will see what happens when that freedom is taken away.

Complexity: sort `O(n log n)`, sweep `O(n)`, space `O(n)`.

### Traps

- **Dividing by zero.** An item of weight 0 has infinite density; take it for free first. Real problems usually promise `w_i > 0`.
- **Wrong key.** Sorting by value alone, or by weight alone, is wrong. Test it.

```python
def knapsack_by_key(items, capacity, key):
    total, room = 0.0, capacity
    for value, weight in sorted(items, key=key, reverse=True):
        part = min(weight, room)
        total += value * part / weight
        room -= part
    return total

things = [(10, 1), (50, 50), (1, 1)]     # one item is huge but thin
print("by density:", knapsack_by_key(things, 50, key=lambda x: x[0] / x[1]))
print("by value  :", knapsack_by_key(things, 50, key=lambda x: x[0]))
```
```text
by density: 59.0
by value  : 50.0
```

Sorting by value takes the heavy `(50, 50)` first and fills the bag with value 50. Density order takes `(10, 1)` first (density 10). The other two items tie at density 1, so it makes no difference which comes next: the bag ends up with the first item plus 49 more kilograms worth 1 each, for a total of 59.

### Predict the output 4

```python
print(fractional_knapsack([(30, 5), (20, 10)], 8)[0])
print(fractional_knapsack([(30, 5), (20, 10)], 100)[0])
```
<details><summary>Answer</summary>

```text
36.0
50.0
```

Densities 6 and 2. With room 8: take all of item 0 (value 30, room 3 left), then `3/10` of item 1, worth 6. Total 36. With room 100 everything fits: 30 + 20 = 50.

</details>

## 8. When greedy fails: 0/1 knapsack

Now change one word in the problem: the thief must take each item **whole or not at all**. This is the **0/1 knapsack**. It looks almost the same. Let us apply the same density rule.

```python
def knapsack_greedy_01(items, capacity):
    total, room = 0, capacity
    for value, weight in sorted(items, key=lambda x: x[0] / x[1], reverse=True):
        if weight <= room:          # take it whole, or skip it
            total += value
            room -= weight
    return total

def knapsack_brute_01(items, capacity):
    best = 0
    for mask in range(1 << len(items)):
        w = sum(items[i][1] for i in range(len(items)) if mask >> i & 1)
        v = sum(items[i][0] for i in range(len(items)) if mask >> i & 1)
        if w <= capacity:
            best = max(best, v)
    return best

items = [(60, 10), (100, 20), (120, 30)]
print("greedy by density:", knapsack_greedy_01(items, 50))
print("true best        :", knapsack_brute_01(items, 50))
```
```text
greedy by density: 160
true best        : 220
```

Greedy takes the two densest items (value 160, weight 30) and then the third item no longer fits, so 20 kilograms of the bag stay **empty**. The best answer is items 1 and 2 (value 220, weight 50): it uses every kilogram. In the fractional version we could fill those last 20 kilograms with a piece of item 2. In the 0/1 version we cannot, and the empty space is exactly the loss.

### Why the exchange argument breaks

In the fractional proof we removed `d` units of a weaker item and put in `d` units of a denser one. Here items come in indivisible lumps, so "remove a little" is illegal; swapping a whole item `b` out for a whole item `a` changes the total weight and may not fit. The proof step that made greedy correct is simply unavailable. Whenever a proof needs *any amount*, check whether the problem allows *any amount*.

### What to do instead

- For 0/1 knapsack the exact answer needs **dynamic programming** (a later module): it considers, for each item and each capacity, both choices (take or skip).
- For tiny `n` (say up to 20), brute force over subsets as above is fine.
- Greedy gives a quick **approximation**: take the better of "density greedy" and "the single most valuable item that fits". This is guaranteed to get at least half the optimum, but not the optimum.

### A second counterexample: the best-value-first trap

```python
bad = [(10, 6), (7, 5), (7, 5)]       # (value, weight), capacity 10
print("greedy by density:", knapsack_greedy_01(bad, 10), " best:", knapsack_brute_01(bad, 10))
```
```text
greedy by density: 10  best: 14
```

The first item has the highest density, `10/6 = 1.67`, against `7/5 = 1.4` for the others, so greedy takes it. Then neither 5-kilogram item fits (6 + 5 = 11 > 10), leaving value 10. The best is the two smaller items together: weight 10, value 14. One dense but awkward item blocks two items that fit together perfectly.

### Summary of the difference

| | Fractional knapsack | 0/1 knapsack |
|---|---|---|
| Can take part of an item? | yes | no |
| Density-greedy correct? | **yes** | **no** |
| Technique | greedy, `O(n log n)` | dynamic programming |
| Why | exchange of any amount of weight is legal | indivisible lumps leave wasted space |

## 9. Coin change: greedy works, but only for some coin systems

### The question

Given coin values and an amount, use the **fewest coins** to pay the amount exactly. We saw in section 1 that "largest coin first" works for the usual money and fails for `[1, 3, 4]`. A system where greedy is always optimal is called **canonical**. Which systems are canonical?

To decide that we need a ground truth that is always right. We can get one from a graph idea you know (dsa.12): treat each amount as a vertex, each coin as an edge from `a` to `a + coin`, and search with **BFS**. The fewest coins to reach `amount` is the BFS distance from 0. BFS is slow-ish, `O(amount * coins)`, but always correct for coins that are positive whole numbers.

```python
from collections import deque

def min_coins_bfs(amount, coins):
    """Fewest coins to make `amount`, or -1 if impossible. Always correct."""
    dist = {0: 0}
    queue = deque([0])
    while queue:
        a = queue.popleft()
        if a == amount:
            return dist[a]
        for c in coins:
            nxt = a + c
            if nxt <= amount and nxt not in dist:
                dist[nxt] = dist[a] + 1
                queue.append(nxt)
    return -1

def min_coins_greedy(amount, coins):
    """Largest coin first. Returns the coin count, or -1 if greedy got stuck."""
    count = 0
    for c in sorted(coins, reverse=True):
        count += amount // c            # how many of this coin fit
        amount %= c
    return count if amount == 0 else -1

print("6  with (1,3,4)  : greedy", min_coins_greedy(6, [1, 3, 4]), " true", min_coins_bfs(6, [1, 3, 4]))
print("30 with (1,10,25) : greedy", min_coins_greedy(30, [1, 10, 25]), " true", min_coins_bfs(30, [1, 10, 25]))
print("9  with (1,3,4)   : greedy", min_coins_greedy(9, [1, 3, 4]), " true", min_coins_bfs(9, [1, 3, 4]))
```
```text
6  with (1,3,4)  : greedy 3  true 2
30 with (1,10,25) : greedy 6  true 3
9  with (1,3,4)   : greedy 3  true 3
```

Note how `amount // c` and `amount %= c` replace the inner `while` loop of section 1: taking as many of the coin as possible in one step (integer division, then the remainder). Same algorithm, faster.

### Greedy can also fail to find any answer

Without a coin of value 1, the largest-first rule may get stuck even though an answer exists.

```python
coins = [5, 3]
print("greedy:", min_coins_greedy(9, coins), "| true:", min_coins_bfs(9, coins))
```
```text
greedy: -1 | true: 3
```

Greedy takes one 5, then one 3, and is left with 1, which no coin can pay (it prints -1 for "stuck"). But `3 + 3 + 3 = 9`. Greedy committed to the 5 and had no way back.

### Which systems are safe?

The usual money systems are safe. Let us confirm a few with the BFS check over many amounts, and let us also find the *first* amount where each unsafe system fails.

```python
def first_failure(coins, limit):
    for amount in range(1, limit + 1):
        if min_coins_greedy(amount, coins) != min_coins_bfs(amount, coins):
            return amount
    return None

systems = {
    "India (1,2,5,10,20,50,100,200)": [1, 2, 5, 10, 20, 50, 100, 200],
    "US (1,5,10,25)": [1, 5, 10, 25],
    "powers of 2 (1,2,4,8,16)": [1, 2, 4, 8, 16],
    "odd (1,3,4)": [1, 3, 4],
    "odd (1,10,25)": [1, 10, 25],
    "odd (1,5,6,9)": [1, 5, 6, 9],
}
for name, coins in systems.items():
    print(f"{name:32} first amount where greedy loses: {first_failure(coins, 150)}")
```
```text
India (1,2,5,10,20,50,100,200)   first amount where greedy loses: None
US (1,5,10,25)                   first amount where greedy loses: None
powers of 2 (1,2,4,8,16)         first amount where greedy loses: None
odd (1,3,4)                      first amount where greedy loses: 6
odd (1,10,25)                    first amount where greedy loses: 30
odd (1,5,6,9)                    first amount where greedy loses: 11
```

The first three are canonical, at least up to 150. The other three break at small amounts: 6 for `(1,3,4)`, 30 for `(1,10,25)` and 11 for `(1,5,6,9)`. Let us look at the numbers around that last one.

```python
for amount in (10, 11, 12):
    print(amount, "greedy:", min_coins_greedy(amount, [1, 5, 6, 9]), "true:", min_coins_bfs(amount, [1, 5, 6, 9]))
```
```text
10 greedy: 2 true: 2
11 greedy: 3 true: 2
12 greedy: 4 true: 2
```

For 10, greedy (9 + 1) and the true answer (5 + 5) both use 2 coins. For 11, greedy takes 9 and then two 1s (3 coins) but `5 + 6` uses 2. For 12, greedy takes 9 and three 1s (4 coins) but `6 + 6` uses 2. A system can behave well on many amounts and still fail on one: one failing amount is enough to make the rule wrong.

### A known fact: you only have to check small amounts

You may wonder how far to test. There is a theorem (Kozen and Zaks, 1994): if a coin system `c1 < c2 < ... < ck` with `c1 = 1` is **not** canonical, then the smallest amount where greedy loses is **less than `c_{k-1} + c_k`**, the sum of the two largest coins. So testing amounts below that bound is a complete test. We check this on random coin systems.

```python
import random

def canonical(coins):
    coins = sorted(coins)
    bound = coins[-1] + (coins[-2] if len(coins) > 1 else 0)
    return first_failure(coins, bound - 1) is None

random.seed(7)
disagreements = 0
for _ in range(300):
    k = random.randint(2, 5)
    coins = sorted(random.sample(range(2, 40), k - 1) + [1])
    if canonical(coins) != (first_failure(coins, 200) is None):
        disagreements += 1
print("systems where the bound-based test disagreed with testing up to 200:", disagreements)
print(canonical([1, 2, 5, 10]), canonical([1, 3, 4]), canonical([1, 5, 10, 25]))
```
```text
systems where the bound-based test disagreed with testing up to 200: 0
True False True
```

In the course you do not need to memorise the theorem. What matters: **greedy coin change is a property of the coin system, not of the algorithm.** Always say which coin system the problem uses. If the problem lets the coins be arbitrary, use BFS or dynamic programming.

### Why does it work for 1, 2, 5, 10, ...?

A sketch of the exchange argument for `(1, 5, 10, 25)`: look at an optimal answer for some amount. It never uses five 1s (replace them by one 5, fewer coins). It never uses two 5s (replace by one 10). It never uses three 10s (25 + 5 is better) and so on. So in an optimal answer every smaller coin appears only a limited number of times, and those limits force the number of large coins to be exactly the greedy number. For `(1, 3, 4)` the argument stops: two 3s (`3 + 3 = 6`) beat `4 + 1 + 1`, and there is no rule that removes them.

### Predict the output 5

```python
print(min_coins_greedy(14, [1, 7, 10]), min_coins_bfs(14, [1, 7, 10]))
print(min_coins_greedy(14, [1, 2, 5, 10]), min_coins_bfs(14, [1, 2, 5, 10]))
```
<details><summary>Answer</summary>

```text
5 2
3 3
```

With `(1, 7, 10)`: greedy takes 10, then four 1s: five coins. But `7 + 7` is two coins. With the usual `(1, 2, 5, 10)`: 10 + 2 + 2, three coins; greedy and BFS agree.

</details>

## 10. Scheduling: which job first?

Scheduling problems ask for the **best order** to do jobs. They are a rich source of greedy algorithms, and also of wrong ones, because every ordering rule sounds sensible. For each problem the method is the same: guess a rule, test it against brute force on tiny inputs, then prove it with an **adjacent swap**.

### Shortest job first: minimising total waiting time

One machine, `n` jobs, each with a duration. A job's **waiting time** is the sum of the durations of the jobs before it. In what order should we run the jobs so that the **total waiting time** is smallest?

```python
from itertools import permutations

def total_waiting(durations):
    wait = 0
    elapsed = 0
    for d in durations:
        wait += elapsed          # this job waited for everything before it
        elapsed += d
    return wait

jobs = [6, 8, 7, 3]
print("as given   :", total_waiting(jobs))
print("shortest 1st:", total_waiting(sorted(jobs)))
print("longest 1st :", total_waiting(sorted(jobs, reverse=True)))
print("brute force :", min(total_waiting(p) for p in permutations(jobs)))
```
```text
as given   : 41
shortest 1st: 28
longest 1st : 44
brute force : 28
```

Sorting by duration (shortest job first, SJF) matches the brute-force minimum. The hand trace for `[3, 6, 7, 8]`: job 3 waits 0; job 6 waits 3; job 7 waits `3 + 6 = 9`; job 8 waits `3 + 6 + 7 = 16`. Total `0 + 3 + 9 + 16 = 28`.

#### Why: the adjacent swap

Suppose two neighbouring jobs `a` then `b` have durations `da > db` (the longer one runs first). Swap them. Every job before them and every job after them is unaffected: the pair together still takes `da + db`, so everything after waits the same as before. Inside the pair, before the swap `b` waits `da` extra; after the swap `a` waits `db` extra. Since `db < da`, the total waiting went **down**. So any order with a longer job directly before a shorter one can be improved, and the only order with no such pair is the sorted one.

This "swap neighbours that are out of order" is the cleanest exchange argument for scheduling. Memorise its steps: (1) look at two adjacent jobs, (2) show the rest is unaffected, (3) show the swap does not hurt.

### The wrong key: jobs with weights

Now each job also has an **importance** (weight). The cost is `sum(weight * finish_time)`, so important jobs should finish early. Which key? Try the three obvious ones.

```python
def weighted_cost(order):
    """order: list of (time, weight). Sum of weight * finish time."""
    t = 0
    total = 0
    for time, weight in order:
        t += time
        total += weight * t
    return total

def best_order_cost(jobs):
    return min(weighted_cost(p) for p in permutations(jobs))

# (time, weight)
case1 = [(3, 10), (1, 1)]       # a long, very important job and a short, trivial one
case2 = [(10, 2), (1, 1)]       # a long, fairly important job and a short, trivial one

for name, jobs in (("case1", case1), ("case2", case2)):
    shortest = sorted(jobs, key=lambda j: j[0])
    heaviest = sorted(jobs, key=lambda j: -j[1])
    ratio    = sorted(jobs, key=lambda j: j[0] / j[1])
    print(name, "shortest:", weighted_cost(shortest), "| heaviest:", weighted_cost(heaviest),
          "| time/weight:", weighted_cost(ratio), "| best:", best_order_cost(jobs))
```
```text
case1 shortest: 41 | heaviest: 34 | time/weight: 34 | best: 34
case2 shortest: 23 | heaviest: 31 | time/weight: 23 | best: 23
```

In `case1`, "shortest first" loses (it runs the trivial job first and delays the important one). In `case2`, "heaviest first" loses (it runs the long job of weight 2 first, and the tiny job waits for 10 units). The ratio `time / weight`, smaller first, wins both. This is **Smith's rule**. Intuition: `time / weight` is "how much time you pay per unit of importance". Do the cheapest-to-finish-per-importance first.

The adjacent swap proves it. Jobs `i` then `j` at the start of some time `T`: the cost of the pair is `w_i(T + t_i) + w_j(T + t_i + t_j)`. After swapping it is `w_j(T + t_j) + w_i(T + t_i + t_j)`. The difference is `w_j * t_i - w_i * t_j`. The original order is better when `w_j * t_i < w_i * t_j`, i.e. `t_i / w_i < t_j / w_j`. Exactly the ratio rule.

If you want to avoid floating-point division, compare with cross-multiplication, or use `fractions.Fraction`. For small whole numbers `t / w` is fine.

### Scheduling with deadlines and profits (job sequencing)

Each job takes exactly **one time unit**, has a **deadline** (it must start in a time slot `1..deadline`) and a **profit**. Only one job can run per slot. Choose which jobs to run, and when, to maximise total profit. Jobs that miss their deadline earn nothing, so we may skip some.

Greedy rule: consider jobs by **profit, highest first**. Put each job in the **latest free slot** at or before its deadline (keeping early slots free for jobs with tighter deadlines). If no slot is free, skip the job.

```python
def job_sequencing(jobs):
    """jobs: list of (name, deadline, profit). Returns (total profit, schedule)."""
    horizon = max(d for _, d, _ in jobs)
    slot = [None] * (horizon + 1)            # slot[1..horizon]
    total = 0
    for name, deadline, profit in sorted(jobs, key=lambda j: -j[2]):
        for t in range(min(deadline, horizon), 0, -1):    # latest free slot first
            if slot[t] is None:
                slot[t] = name
                total += profit
                break
    return total, slot[1:]

jobs = [("a", 2, 100), ("b", 1, 19), ("c", 2, 27), ("d", 1, 25), ("e", 3, 15)]
print(job_sequencing(jobs))
```
```text
(142, ['c', 'a', 'e'])
```

Hand trace in profit order: `a` (100, deadline 2) goes to slot 2. `c` (27, deadline 2): slot 2 is taken, slot 1 is free, so it takes slot 1. `d` (25, deadline 1): slot 1 is taken, nothing earlier exists, skip. `b` (19, deadline 1): same, skip. `e` (15, deadline 3): slot 3 is free. Schedule: `c, a, e` for `27 + 100 + 15 = 142`.

Why "the latest free slot"? Because an early slot is a scarce resource: only jobs with early deadlines can use it. Putting a job in the latest slot it is allowed keeps the scarce early slots free for others. Why "highest profit first"? Exchange argument: if the best schedule skips the most profitable job `x` that could be scheduled while it keeps a cheaper job `y` in a slot `x` could use, swap them. Profit does not decrease.

The slot search makes this `O(n * horizon)` in the worst case, which is `O(n^2)` once you cap each deadline at `n` (a job can never use a slot later than the `n`-th). A **union-find** structure (dsa.12 section 9) that links each full slot to the previous slot finds the latest free slot in almost constant time and brings the total to `O(n log n)`, the cost of the sort.

#### Another way: a heap, by deadline

Sort the jobs by deadline instead. Keep a **min-heap of profits** of the jobs we currently plan to do. Each job joins the heap. If the heap now holds more jobs than the job's deadline allows (`len(heap) > deadline`), the plan is overfull, so throw away the **least profitable** job (the heap's root).

```python
import heapq

def job_sequencing_heap(jobs):
    heap = []
    for name, deadline, profit in sorted(jobs, key=lambda j: j[1]):
        heapq.heappush(heap, profit)
        if len(heap) > deadline:
            heapq.heappop(heap)           # drop the cheapest planned job
    return sum(heap)

print(job_sequencing_heap(jobs))
```
```text
142
```

Trace by deadline: `b`(1, 19): heap [19], size 1 <= 1. `d`(1, 25): heap [19, 25], size 2 > 1, pop 19 -> [25]. `a`(2, 100): heap [25, 100], size 2 <= 2. `c`(2, 27): heap [25, 27, 100], size 3 > 2, pop 25 -> [27, 100]. `e`(3, 15): heap [15, 27, 100], size 3 <= 3. Sum: 142. Time `O(n log n)`, space `O(n)`. This version tells you the total but not the slots; if you need the schedule, use the slot version.

A random test against brute force (every subset, then check whether it can be scheduled by sorting by deadline):

```python
import random

def jobs_brute(jobs):
    best = 0
    for mask in range(1 << len(jobs)):
        chosen = sorted((jobs[i] for i in range(len(jobs)) if mask >> i & 1), key=lambda j: j[1])
        if all(k + 1 <= j[1] for k, j in enumerate(chosen)):      # k-th job (0-based) runs in slot k+1
            best = max(best, sum(j[2] for j in chosen))
    return best

random.seed(3)
bad = 0
for _ in range(500):
    n = random.randint(1, 8)
    js = [(i, random.randint(1, 5), random.randint(1, 50)) for i in range(n)]
    want = jobs_brute(js)
    if job_sequencing(js)[0] != want or job_sequencing_heap(js) != want:
        bad += 1
print("mismatches in 500 random cases:", bad)
```
```text
mismatches in 500 random cases: 0
```

### Minimising the maximum lateness

Jobs have a duration and a due time (deadline). All must run, one after another, without gaps. A job's **lateness** is `max(0, finish - deadline)`. Minimise the **largest** lateness.

Rule: **earliest deadline first (EDF)**. Notice that durations are ignored in the key. A job with a distant deadline can wait however long it is.

```python
def max_lateness(order):
    """order: list of (duration, deadline)."""
    t = 0
    worst = 0
    for duration, deadline in order:
        t += duration
        worst = max(worst, t - deadline)
    return worst

jobs = [(3, 6), (2, 8), (1, 9), (4, 9), (3, 14), (2, 15)]
edf = sorted(jobs, key=lambda j: j[1])
print(edf)
print("EDF max lateness:", max_lateness(edf))
print("brute force     :", min(max_lateness(p) for p in permutations(jobs)))

hard = [(5, 5), (1, 6)]
print("shortest first:", max_lateness(sorted(hard)), "| EDF:", max_lateness(sorted(hard, key=lambda j: j[1])))
```
```text
[(3, 6), (2, 8), (1, 9), (4, 9), (3, 14), (2, 15)]
EDF max lateness: 1
brute force     : 1
shortest first: 1 | EDF: 0
```

Adjacent swap proof: if job `a` runs just before `b` but `a`'s deadline is later than `b`'s (an "inversion"), swap them. The pair together ends at the same time as before. The job moved earlier (`b`) can only become less late. The job moved later (`a`) ends at the old pair end, which is the same time `b` used to end, but `a`'s deadline is later than `b`'s, so `a`'s new lateness is at most `b`'s old lateness. The maximum does not rise.

The function starts `worst` at 0, so a printed 0 means nobody is late. In the last test, running the short job first makes the 5-unit job finish at time 6, one unit late; EDF runs the 5-unit job first and nobody is late.

### Predict the output 6

```python
print(total_waiting([2, 1, 3]))
print(total_waiting(sorted([2, 1, 3])))
```
<details><summary>Answer</summary>

```text
5
4
```

Order `[2, 1, 3]`: waits are 0, 2, 3, total 5. Sorted `[1, 2, 3]`: waits are 0, 1, 3, total 4.

</details>

## 11. Greedy on arrays

The array problems below look different, but each is a one-pass greedy that keeps a tiny amount of state ("farthest reach", "current tank", "pointer to the smallest cookie"). For each one, ask: **what is the state, and why is forgetting everything else safe?**

### Assign cookies

Each child `i` has a greed `g[i]`: the smallest cookie size that makes them happy. Each cookie `j` has a size `s[j]`. A child gets at most one cookie, and a cookie goes to at most one child. Maximise the number of happy children.

Greedy: sort both. Walk through the cookies from the smallest. Each cookie goes to the **least greedy child who is still unhappy**, if it is big enough; otherwise this cookie is too small for everyone left, so discard it.

```python
def assign_cookies(greed, sizes):
    greed = sorted(greed)
    sizes = sorted(sizes)
    child = 0
    for cookie in sizes:
        if child < len(greed) and cookie >= greed[child]:
            child += 1                  # this child is happy; move to the next child
    return child

print(assign_cookies([1, 2, 3], [1, 1]))
print(assign_cookies([1, 2], [1, 2, 3]))
print(assign_cookies([10, 9, 8, 7], [5, 6, 7, 8]))
```
```text
1
2
2
```

Trace the first call. Greed sorted `[1, 2, 3]`, cookies `[1, 1]`. Cookie 1 satisfies child 0 (greed 1): `child = 1`. The next cookie 1 is smaller than greed 2: not used. One happy child. In the last call: cookies 5 and 6 are too small for greed 7. Cookie 7 satisfies greed 7. Cookie 8 satisfies greed 8. Two happy.

Why safe? A small cookie that satisfies any child should satisfy the **least greedy** remaining one: giving it to a greedier child is either impossible or wasteful (exchange: the least greedy child could have used it, and the greedy one then gets a bigger cookie at least as good). Cost `O(n log n + m log m)`.

### Jump game: can I reach the last index?

`nums[i]` is the maximum jump length from index `i`. Starting at index 0, can you reach the last index?

Track `farthest`: the furthest index reachable so far. Visit indices left to right; if an index is beyond `farthest`, we are stuck.

```python
def can_jump(nums):
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest:
            return False
        farthest = max(farthest, i + jump)
    return True

print(can_jump([2, 3, 1, 1, 4]))
print(can_jump([3, 2, 1, 0, 4]))
print(can_jump([0]))
```
```text
True
False
True
```

Trace `[3, 2, 1, 0, 4]`: i=0, farthest becomes 3. i=1: 1+2=3. i=2: 2+1=3. i=3: 3+0=3. i=4: 4 > 3, stuck. The zero at index 3 is a wall that every path lands on.

Why a single number is enough: the set of reachable indices is always a prefix `0..farthest` with no gaps (if you can reach index 5 with a jump of at most `nums[k]`, you can also land on every index between `k` and 5). So knowing only the far end loses nothing. Time `O(n)`, space `O(1)`.

### Jump game II: the fewest jumps

Same array, but now count the **minimum number of jumps** to reach the last index (assume it is reachable). Think of it as BFS in layers: the indices reachable in 1 jump, then those reachable in 2 jumps, and so on. Each layer is an interval, so we need only its end.

```python
def min_jumps(nums):
    jumps = 0
    layer_end = 0          # furthest index reachable with `jumps` jumps
    farthest = 0           # furthest index reachable with `jumps + 1` jumps
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == layer_end:           # we must jump now to go any further
            jumps += 1
            layer_end = farthest
    return jumps

print(min_jumps([2, 3, 1, 1, 4]))
print(min_jumps([2, 3, 0, 1, 4]))
print(min_jumps([1, 1, 1, 1]))
print(min_jumps([0]))
```
```text
2
2
3
0
```

Trace `[2, 3, 1, 1, 4]`. i=0: farthest 2; i equals `layer_end` 0: jumps 1, layer_end 2. i=1: farthest max(2, 4)=4. i=2: farthest 4; i equals layer_end: jumps 2, layer_end 4. i=3: farthest stays 4, and `i` (3) is not `layer_end` (4), so no jump. The loop ends at index 3 because we never need to jump *from* the last index. Answer 2.

Rule of thumb: we delay each jump until it is forced, and when forced we jump to the position that reaches the farthest. That is the exchange argument: any jump that lands somewhere else reaches no farther.

### Gas station

`n` stations on a circle. At station `i` you get `gas[i]` litres, and driving to the next station costs `cost[i]`. The tank starts empty and has unlimited size. Find the index to start at to go all the way round, or `-1`.

Two facts make this a one-pass greedy.

1. If `sum(gas) < sum(cost)`, the answer is `-1`: there simply is not enough fuel in the whole circle.
2. Otherwise a start exists. Run along from station 0 keeping the tank. If the tank goes **negative** at station `i`, then no station between the current start and `i` can be a valid start. Why: a later start `k` in that range begins with an empty tank, but the current start reached `k` with a tank that was still `>= 0`, so starting at `k` is never better and it also fails at `i`. So **restart from `i + 1`** with an empty tank.

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = 0
    start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:            # cannot get past station i from `start`
            start = i + 1       # so no station up to i works
            tank = 0
    return start

print(can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]))
print(can_complete_circuit([2, 3, 4], [3, 4, 3]))
print(can_complete_circuit([5], [4]))
```
```text
3
-1
0
```

Trace the first one. Net gain per station (`gas - cost`) is `[-2, -2, -2, 3, 3]`. Total 0 >= 0, so a solution exists. i=0: tank -2 < 0, start = 1, tank 0. i=1: -2, start 2. i=2: -2, start 3. i=3: tank 3. i=4: tank 6. Return 3. (From station 3, the tank goes 3, 6, then it reaches stations 0, 1, 2 with 6 - 2 = 4, 2, 0, never negative.)

Why is the final `start` right? The total is nonnegative, so the stretch after the last failing point must hold enough surplus to pay for all earlier deficits. Time `O(n)`, space `O(1)`.

### Best time to buy and sell stock (many trades)

You may buy and sell as often as you like, one share at a time. Maximise the total profit. Greedy: add every positive day-to-day rise, because a long rise is the sum of its daily rises.

```python
def max_profit(prices):
    return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))

print(max_profit([7, 1, 5, 3, 6, 4]))
print(max_profit([1, 2, 3, 4, 5]))
print(max_profit([5, 4, 3, 2, 1]))
```
```text
7
4
0
```

For `[7, 1, 5, 3, 6, 4]`: rises are `1 to 5` (4) and `3 to 6` (3): total 7. For `[1,2,3,4,5]` the rises are `1+1+1+1 = 4`, the same as buying at 1 and selling at 5.

Notice the contrast with the version that allows **one** trade: that is not this greedy, it needs a running minimum. Always read how many transactions the problem allows.

### Lemonade change: a greedy with a preference

Customers pay with 5, 10 or 20 for a 5-rupee lemonade. You start with no cash. Can you give correct change to every customer in order? The only real choice is a 20: change is 15, either `10 + 5` or `5 + 5 + 5`. Which one to give?

Prefer `10 + 5`: fives are the most useful coin (they can be used for both 10s and 20s), tens are only useful for 20s. So spend the less flexible resource first.

```python
def lemonade(bills):
    five = ten = 0
    for b in bills:
        if b == 5:
            five += 1
        elif b == 10:
            if five == 0:
                return False
            five -= 1
            ten += 1
        else:                                # 20: change is 15
            if ten and five:
                ten -= 1
                five -= 1                    # prefer 10 + 5
            elif five >= 3:
                five -= 3
            else:
                return False
    return True

print(lemonade([5, 5, 5, 10, 20]))
print(lemonade([5, 5, 10, 10, 20]))
```
```text
True
False
```

In the second case, the first two fives give `five = 2`. The first 10 takes a five (`five = 1, ten = 1`), the second 10 takes the last five (`five = 0, ten = 2`). The 20 needs 15 in change: there are tens but no five, and fewer than three fives, so it is impossible. Result `False`.

Does the preference matter? Compare with the "obvious" rule that always tries three fives first:

```python
def lemonade_fives_first(bills):
    five = ten = 0
    for b in bills:
        if b == 5:
            five += 1
        elif b == 10:
            if five == 0:
                return False
            five -= 1
            ten += 1
        else:
            if five >= 3:
                five -= 3                    # spends three of the most useful bills
            elif ten and five:
                ten -= 1
                five -= 1
            else:
                return False
    return True

case = [5, 5, 5, 5, 10, 20, 10]
print("prefer 10+5:", lemonade(case), "| fives first:", lemonade_fives_first(case))
```
```text
prefer 10+5: True | fives first: False
```

Trace the failing rule. Four fives. The 10 takes a five: `five = 3, ten = 1`. The 20 sees three fives and spends them all: `five = 0, ten = 1`. The last 10 needs a five: none left. Failure. The good rule spends the 10 and one five on the 20, leaving `five = 2`, which pays for the last 10. Spend the resource that is **less flexible** first.

## 12. Greedy on numbers and strings

Two short examples where the greedy key or the greedy invariant is not obvious.

### The largest number from a list

Given non-negative integers, arrange them so the concatenation is as large as possible. `[3, 30, 34, 5, 9]` should give `9534330`. Sorting numerically or alphabetically does not work (`30` versus `3`). The right comparison: put `a` before `b` if the string `a + b` is bigger than `b + a`.

```python
from functools import cmp_to_key

def largest_number(nums):
    strs = [str(n) for n in nums]
    def compare(a, b):
        if a + b > b + a:
            return -1            # a comes first
        if a + b < b + a:
            return 1
        return 0
    strs.sort(key=cmp_to_key(compare))
    result = "".join(strs)
    return "0" if result[0] == "0" else result      # [0, 0] -> "0", not "00"

print(largest_number([3, 30, 34, 5, 9]))
print(largest_number([0, 0]))
print(largest_number([10, 2]))
print("plain string sort would give:", "".join(sorted(map(str, [3, 30, 34, 5, 9]), reverse=True)))
```
```text
9534330
0
210
plain string sort would give: 9534303
```

The plain descending text sort gives `9534303` and the pairwise rule gives `9534330`. The difference is the order of `3` and `30`. As text, `"30"` is bigger than `"3"` (a longer string with the same start is bigger), so the plain sort puts `30` first. But `"3" + "30" = "330"` is bigger than `"30" + "3" = "303"`, so `3` must come first. The pairwise rule compares the two **concatenations**, which is the actual quantity we are maximising. The order it defines is consistent (transitive), which a sort needs. This is a custom comparator from dsa.05 section 15, used as a greedy key.

### Remove K digits: the smallest number left

Given a string of digits and `k`, remove exactly `k` digits so the remaining number is as small as possible.

Greedy: scan left to right with a stack. Whenever the next digit is **smaller** than the stack's top, the top is making the number bigger than it has to be (a bigger digit sits in a more significant place than a smaller one), so pop it, as long as removals remain. At the end, remove any leftover removals from the end.

```python
def remove_k_digits(num, k):
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    if k:
        stack = stack[:-k]               # remaining removals come off the right end
    return "".join(stack).lstrip("0") or "0"

print(remove_k_digits("1432219", 3))
print(remove_k_digits("10200", 1))
print(remove_k_digits("10", 2))
print(remove_k_digits("12345", 2))
```
```text
1219
200
0
123
```

Trace `"1432219"` with `k = 3`. Push 1. Push 4. Next 3 < 4: pop 4 (k=2), push 3. Next 2 < 3: pop 3 (k=1), push 2. Next 2: not smaller, push. Next 1 < 2: pop 2 (k=0), push 1. Next 9: push. Stack `1 2 1 9`: "1219". The case `"10200"` with `k = 1`: push 1; next 0 < 1: pop 1, push 0; then 2, 0, 0 pushed: "00200", strip leading zeros: "200". And `"12345"` never pops (digits only rise), so the two removals come off the right end: "123".

Why greedy? The leftmost digit has the highest weight. If a digit is followed by a smaller digit, deleting it makes the number smaller no matter what comes later, so it is always safe. Time `O(n)` since each digit is pushed and popped at most once.

## 13. Huffman coding

### The problem: shorter codes for common letters

Computers store text with fixed-size codes: 8 bits for every character (ASCII), or fewer if the alphabet is small. But letters are not equally common. In English text, `e` appears far more often than `z`. If common letters got short codes and rare letters got long ones, the file would shrink.

The catch is that codes of different lengths can become ambiguous. Suppose `a = 0`, `b = 01`, `c = 1`. The bits `01` could mean `b`, or `a` followed by `c`.

```python
code = {"a": "0", "b": "01", "c": "1"}

def encode(text, code):
    return "".join(code[ch] for ch in text)

print(encode("b", code), encode("ac", code))
```
```text
01 01
```

Both texts give the same bits `01`. We cannot tell which was sent.

### Prefix-free codes

The fix: make sure **no code is the beginning (prefix) of another code**. Then, reading bits from left to right, the moment the bits read so far match a code, that code is the answer, and nothing else could still be coming. A prefix-free code can be drawn as a **binary tree**: each letter sits at a **leaf**, going left appends `0`, and going right appends `1`. A letter at a leaf can never be a prefix of another letter's path, since leaves have no children.

```text
          (root)
          /    \
        0/      \1
        a        (.)
                 /  \
               0/    \1
               b      c

    a = 0     b = 10     c = 11
```

Reading `10 0 11` gives `b`, `a`, `c` with no doubt.

### What is the cost of a tree?

If letter `x` occurs `f(x)` times and sits at depth `d(x)` (its code has `d(x)` bits), the encoded file has

```text
cost = sum over letters of  f(x) * d(x)   bits
```

We want the tree that minimises this. Notice the pull of the formula: a letter with a large `f` should have a small `d`.

### The greedy algorithm (Huffman, 1952)

1. Make a leaf for each letter, with its frequency as weight.
2. Take the **two lightest** trees. Join them under a new parent whose weight is the sum.
3. Repeat step 2 until there is a single tree.

The two rarest letters end up deepest (they are joined first, so they are buried under all the later joins), and the commonest letters are joined last, near the root. This is exactly the "connect the sticks" problem from dsa.11 section 10: the total cost of all joins equals the cost of the tree.

### Hand-traced example

Frequencies (per 100 letters): `a:45, b:13, c:12, d:16, e:9, f:5`. We keep a sorted list of weights and merge the two smallest each round.

```python
freq = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
weights = sorted(freq.values())
total_cost = 0
round_no = 1
while len(weights) > 1:
    x, y = weights[0], weights[1]
    print(f"round {round_no}: weights {weights} -> join {x} + {y} = {x + y}")
    total_cost += x + y
    weights = sorted(weights[2:] + [x + y])
    round_no += 1
print("final weights:", weights, "| sum of all joins:", total_cost)
```
```text
round 1: weights [5, 9, 12, 13, 16, 45] -> join 5 + 9 = 14
round 2: weights [12, 13, 14, 16, 45] -> join 12 + 13 = 25
round 3: weights [14, 16, 25, 45] -> join 14 + 16 = 30
round 4: weights [25, 30, 45] -> join 25 + 30 = 55
round 5: weights [45, 55] -> join 45 + 55 = 100
final weights: [100] | sum of all joins: 224
```

The sum of all joins, 224, is the cost of the tree: 224 bits to store 100 letters, an average of 2.24 bits per letter. A fixed-length code for 6 letters needs 3 bits each: 300 bits. The saving is about 25 percent.

### The implementation with `heapq`

We need "the two smallest" repeatedly, so we use a min-heap (dsa.11). But the tree nodes must be stored in the heap too, and here lies a classic trap.

**The tie-breaker trap.** The natural heap entry is `(weight, tree)`. When two entries have the **same weight**, Python compares the second elements, the trees. If one tree is a letter (a string) and the other is a pair (a tuple), that comparison raises an error.

```python
import heapq

heap = []
try:
    heapq.heappush(heap, (5, "f"))
    heapq.heappush(heap, (5, ("x", "y")))   # same weight 5, but a tuple instead of a string
except TypeError as err:
    print("TypeError:", err)
```
```text
TypeError: '<' not supported between instances of 'tuple' and 'str'
```

(The exact wording of the message depends on your Python version; the type of error does not. The error appears already at the second `heappush`, because a push compares the new entry with its parent in the heap.) Even if the trees were all tuples, comparing them would be slow and meaningless. The cure is to put a **unique integer tie-breaker** between the weight and the tree: `(weight, tie, tree)`. Ties on weight are then decided by the integer, which is always comparable, and the trees themselves are never compared.

```python
import heapq
from collections import Counter

def huffman_tree(freq):
    """freq: dict letter -> count. Returns the root: a letter, or a pair (left, right)."""
    heap = []
    tie = 0
    for letter in sorted(freq):                  # sorted -> same result on every run
        heap.append((freq[letter], tie, letter))
        tie += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        w1, _, t1 = heapq.heappop(heap)
        w2, _, t2 = heapq.heappop(heap)
        heapq.heappush(heap, (w1 + w2, tie, (t1, t2)))
        tie += 1
    return heap[0][2]

def huffman_codes(freq):
    if len(freq) == 1:                           # one letter: it still needs 1 bit
        return {next(iter(freq)): "0"}
    codes = {}
    def walk(tree, prefix):
        if isinstance(tree, str):
            codes[tree] = prefix
        else:
            walk(tree[0], prefix + "0")
            walk(tree[1], prefix + "1")
    walk(huffman_tree(freq), "")
    return codes

codes = huffman_codes(freq)
for letter in sorted(codes, key=lambda x: len(codes[x])):
    print(letter, freq[letter], codes[letter])
print("cost:", sum(freq[x] * len(codes[x]) for x in freq))
```
```text
a 45 0
c 12 100
b 13 101
d 16 111
f 5 1100
e 9 1101
cost: 224
```

The cost, 224, agrees with the hand trace. The most frequent letter `a` has a 1-bit code, and the rarest letters `e` and `f` have 4-bit codes.

#### Why the tie-breaker also makes the output reproducible

Whenever several letters have equal frequency, there is more than one valid Huffman tree: swapping the two children of any node gives another tree with exactly the same cost. Python's `heapq` is deterministic, but only if you give it a total order. The `(weight, tie, tree)` entries have a total order, so the tree built is the same on every run. A different tie rule (for example, numbering the letters in another order) can give different codes for the same text. All of them are optimal. When a test compares *codes*, fix the tie-break rule; when a test compares the *total cost*, any valid rule passes.

```python
same = {"a": 1, "b": 1, "c": 1, "d": 1}
print(huffman_codes(same))
print(huffman_codes({"d": 1, "c": 1, "b": 1, "a": 1}))
```
```text
{'a': '00', 'b': '01', 'c': '10', 'd': '11'}
{'a': '00', 'b': '01', 'c': '10', 'd': '11'}
```

Equal frequencies give a balanced tree: four letters, two bits each. Because we sort the letters before numbering them, the dict passed in any order gives the same codes.

### Encoding and decoding

```python
def encode(text, codes):
    return "".join(codes[ch] for ch in text)

def decode(bits, tree):
    out = []
    node = tree
    for bit in bits:
        node = node[0] if bit == "0" else node[1]        # walk left or right
        if isinstance(node, str):                          # reached a leaf
            out.append(node)
            node = tree                                    # start the next letter at the root
    return "".join(out)

text = "abracadabra"
f = Counter(text)
tree = huffman_tree(f)
codes = huffman_codes(f)
bits = encode(text, codes)
print(codes)
print(bits, len(bits), "bits versus", 8 * len(text), "as 8-bit characters")
print(decode(bits, tree))
```
```text
{'a': '0', 'c': '100', 'd': '101', 'b': '110', 'r': '111'}
01101110100010101101110 23 bits versus 88 as 8-bit characters
abracadabra
```

The round trip works: decoding walks the tree from the root, and each time it lands on a leaf it writes the letter and returns to the root. No separators are needed, because the code is prefix-free. Also notice that the tree must be sent along with the file (or rebuilt from the frequency table), or the receiver cannot decode.

Edge case: a text with a single distinct letter. The tree is just one leaf, so we give it the code `"0"`, otherwise the encoded file would be empty and the length of the text would be lost.

```python
print(huffman_codes({"z": 7}))
print(encode("zzz", huffman_codes({"z": 7})))
```
```text
{'z': '0'}
000
```

### Why Huffman is optimal

The proof uses both ideas of section 3.

1. **Greedy choice.** Let `x` and `y` be the two least frequent letters. Take any optimal tree. Two sibling leaves sit at the deepest level. Exchange `x` and `y` with those two: since `x` and `y` are the rarest, moving them deeper and moving more frequent letters up cannot raise `sum f * d`. So an optimal tree exists where `x` and `y` are deepest siblings.
2. **Optimal substructure.** Replace `x` and `y` by one new letter `z` with frequency `f(x) + f(y)`. The cost of the old tree equals the cost of the new tree plus `f(x) + f(y)` (every bit of `x` and `y` is one bit deeper than `z`). So a tree for the old problem is optimal exactly when the tree for the new, smaller problem is.

We can also test it. Here is a brute-force search that tries **every** possible pair to merge at every step (exponentially many sequences) and returns the cheapest total. Huffman must match it.

```python
import random
from functools import lru_cache

@lru_cache(maxsize=None)
def best_merge_cost(ws):
    """Cheapest total cost over every possible order of joining pairs. ws is a sorted tuple."""
    if len(ws) == 1:
        return 0
    best = float("inf")
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            merged = ws[i] + ws[j]
            rest = [ws[k] for k in range(len(ws)) if k != i and k != j] + [merged]
            best = min(best, merged + best_merge_cost(tuple(sorted(rest))))
    return best

def huffman_cost(weights):
    heap = list(weights)
    heapq.heapify(heap)
    cost = 0
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        cost += a + b
        heapq.heappush(heap, a + b)
    return cost

random.seed(11)
mismatch = 0
for _ in range(200):
    ws = [random.randint(1, 20) for _ in range(random.randint(2, 6))]
    if huffman_cost(ws) != best_merge_cost(tuple(sorted(ws))):
        mismatch += 1
print("mismatches in 200 random cases:", mismatch)
```
```text
mismatches in 200 random cases: 0
```

(`lru_cache` stores the answers of repeated sub-calls so the search is fast enough. You do not need it to understand Huffman; it only speeds up the checking.)

### Complexity

Let `n` be the length of the text and `k` the number of **distinct** letters.

- Counting letters: `O(n)`.
- Building the tree: `k` pushes and `2(k - 1)` pops, each `O(log k)`: `O(k log k)` total.
- Encoding: `O(n)` (one dictionary lookup per letter).
- Space: `O(k)` for the heap and the tree.

For a fixed alphabet (say 256 byte values) the tree-building is a constant, and the whole thing is `O(n)`.

### Predict the output 7

```python
print(huffman_cost([5, 9, 12, 13, 16, 45]))
print(huffman_cost([1, 1, 1, 1]))
print(huffman_cost([7]))
```
<details><summary>Answer</summary>

```text
224
8
0
```

The first list has the same frequencies as the hand-traced example: 224. Four ones: join 1+1=2, 1+1=2, then 2+2=4: cost `2 + 2 + 4 = 8`, which is 4 letters times 2 bits. One letter: nothing to join, so the join cost is 0 (the `0` bit we give a lone letter in `huffman_codes` is a convention for the file format, not part of the join cost).

</details>

## 14. Greedy inside algorithms you already know, and a word on matroids

### Greedy algorithms from earlier modules

You have already met several algorithms whose correctness is a greedy argument. Now you can name the argument.

| Algorithm | Greedy choice | Why it is safe | Module |
|---|---|---|---|
| Kruskal (minimum spanning tree) | cheapest edge that does not close a cycle | **cut property**: the cheapest edge crossing any cut belongs to some MST (exchange argument) | dsa.12 section 15 |
| Prim | cheapest edge leaving the tree built so far | same cut property | dsa.12 section 15 |
| Dijkstra | unvisited vertex with the smallest tentative distance | with non-negative edges, no later path can be shorter; this fails with negative edges | dsa.12 section 10 |
| Merge K sorted lists, connect sticks | smallest available item | heap invariant | dsa.11 |
| Interval merge, meeting rooms | process by start or end time | sorted order | dsa.05 section 16, and section 6 above |

The Dijkstra row deserves a pause. It is greedy, it is optimal on graphs with non-negative edge weights, and with a **negative edge** it fails. The reason is the same as everything else in this chapter: the proof step "no later path can be shorter" used the non-negativity. When an assumption of the proof is removed, the algorithm is wrong.

### Matroids: the structure behind many greedy algorithms (intuition only)

Why does "sort by weight, then add what fits" work for so many unrelated problems? A **matroid** is a collection of "allowed sets" (called independent sets) with two properties:

1. **Hereditary:** any subset of an allowed set is allowed. (If a set of jobs can all meet their deadlines, so can any part of it.)
2. **Exchange:** if one allowed set `A` is smaller than another allowed set `B`, you can always find an element of `B` that you can add to `A` and still be allowed.

Whenever the allowed sets form a matroid, one rule is **guaranteed optimal** for maximising a total weight:

> Sort the elements from heaviest to lightest. Add an element if the set stays allowed. Otherwise skip it.

Examples of matroids: "sets of at most `k` items", "forests (sets of edges with no cycle)" (this is Kruskal, for a maximum or minimum weight), and "sets of unit-time jobs that can all meet their deadlines" (this is job sequencing). Examples that are **not** matroids: knapsack with capacity (a small allowed set and a large one may not exchange nicely, because items have different weights), and coin change.

We can write that rule once and run it on both kinds of problem.

```python
def matroid_greedy(elements, weight, allowed):
    """Heaviest first; keep an element if the chosen set stays allowed."""
    chosen = []
    for e in sorted(elements, key=weight, reverse=True):
        if allowed(chosen + [e]):
            chosen.append(e)
    return chosen

# 1. Job sequencing: (name, deadline, profit). A set is allowed if its jobs can all meet deadlines.
def schedulable(js):
    by_deadline = sorted(js, key=lambda j: j[1])
    return all(k + 1 <= j[1] for k, j in enumerate(by_deadline))

jobs = [("a", 2, 100), ("b", 1, 19), ("c", 2, 27), ("d", 1, 25), ("e", 3, 15)]
picked = matroid_greedy(jobs, weight=lambda j: j[2], allowed=schedulable)
print("jobs:", sum(j[2] for j in picked), sorted(j[0] for j in picked), "| brute force:", jobs_brute(jobs))

# 2. 0/1 knapsack: (value, weight). A set is allowed if the weights fit in the capacity 10.
items = [(10, 6), (7, 5), (7, 5)]
picked = matroid_greedy(items, weight=lambda it: it[0], allowed=lambda s: sum(w for _, w in s) <= 10)
print("knapsack:", sum(v for v, _ in picked), "| brute force:", knapsack_brute_01(items, 10))
```
```text
jobs: 142 ['a', 'c', 'e'] | brute force: 142
knapsack: 10 | brute force: 14
```

The same function is exactly right for the job problem (a matroid) and wrong for knapsack (not a matroid). You do not have to prove a problem is a matroid in practice, but this gives a good feel for the question to ask: **if I have a small feasible set and a bigger feasible set, can I always borrow an element from the bigger one to extend the smaller one?** If that "borrowing" can fail, greedy is in danger.

## 15. How to decide whether greedy works

### A checklist

Work through these in order when you meet a new problem.

1. **Name the choice.** What exactly is chosen at each step? (An item, an interval, a coin, a job, a merge.)
2. **Name the objective.** Minimise or maximise what? Count, sum, maximum, last finishing time? The same input can be greedy-safe for one objective and not for another (section 5, count versus value).
3. **List candidate rules.** Earliest, smallest, biggest, densest, tightest deadline. Write at least three.
4. **Try to break each rule by hand** on 3 to 4 items. Use extremes: one huge item among small ones; ties; items that barely fit; an item that "blocks" two others.
5. **Test against brute force** on thousands of random small inputs (below).
6. **Prove the survivor.** Exchange argument (section 3) for a rule that rearranges an optimal answer into the greedy one; stay-ahead argument for step-by-step comparison; lower-bound argument when you can show greedy reaches a bound no algorithm can beat.
7. **Check the assumptions of the proof.** Non-negative weights? Divisible items? Unit-length jobs? Canonical coins? If the problem statement removes one, the proof is gone.
8. **If it fails: use dynamic programming or search.** A counterexample to greedy does not mean the problem is hard; it means the problem needs a different technique.

### Signs that greedy might work

- The problem asks for the **best set or order** (a selection or a schedule).
- There is a natural **ranking** of the choices (by time, by ratio, by size).
- A choice **never makes the remaining problem harder** than any other choice would.
- A sorted order or heap appears naturally in your thinking.

### Signs that greedy will probably fail

- Choices **interact**: taking an item changes what the other items are worth (knapsack with lumps).
- You need a count of **ways**, not one best answer (counting needs DP).
- The best answer needs **looking ahead**: "take less now to take more later".
- The objective has two competing quantities with a hard limit (value against weight).

### A tool for step 5: a generic stress test

Here is a small harness that runs a greedy and a brute force on random inputs, and returns the first input where they differ. We apply it to two rules for activity scheduling.

```python
import random

def find_counterexample(greedy, brute, make_input, trials=2000, seed=0):
    rng = random.Random(seed)
    for _ in range(trials):
        data = make_input(rng)
        if greedy(data) != brute(data):
            return data, greedy(data), brute(data)
    return None

def random_events(rng):
    n = rng.randint(3, 6)
    out = []
    for _ in range(n):
        s = rng.randint(0, 10)
        out.append((s, s + rng.randint(1, 6)))
    return out

def shortest_first(events):
    return len(pick(events, key=lambda ev: ev[1] - ev[0]))

def earliest_finish(events):
    return len(select_activities(events))

print("shortest first :", find_counterexample(shortest_first, brute_best, random_events))
print("earliest finish:", find_counterexample(earliest_finish, brute_best, random_events))
```
```text
shortest first : ([(1, 7), (1, 7), (5, 9), (8, 9), (5, 9)], 1, 2)
earliest finish: None
```

The harness finds a counterexample for "shortest first" almost at once, and finds none for "earliest finish" in 2000 random trials. The first output is a tuple: the input, what greedy gave, and what brute force gave. Passing a stress test is **not a proof**, but failing one is a proof of failure.

Tips for good stress tests: keep inputs tiny (3 to 8 items) so the brute force is instant; use a small value range so that **ties and duplicates are common**; always fix the random seed so a failure can be reproduced; and keep the brute force simple enough to be obviously right.

### Predict the output 8

```python
coins = [1, 6, 10]
print(min_coins_greedy(12, coins), min_coins_bfs(12, coins))
```
<details><summary>Answer</summary>

```text
3 2
```

Greedy takes 10 and two 1s: three coins. But `6 + 6` is two coins. The system `(1, 6, 10)` is not canonical.

</details>

## 16. Common traps, collected

1. **Assuming greedy works because it feels natural.** The coin change `(1, 3, 4)` and 0/1 knapsack both feel natural and are wrong. Test, then prove.
2. **Sorting by the wrong key.** Activity selection needs the *end* time. Fractional knapsack needs *density*, not value. Weighted completion needs *time / weight*. Write the key, then test it.
3. **Forgetting what touching means.** Half-open intervals (`s >= last_end`) versus closed intervals (`s > shot_at`). Read the statement for "inclusive".
4. **Merging intervals without `max`.** `out[-1][1] = e` loses the case where the new interval is inside the old one. Use `max(out[-1][1], e)`.
5. **Mutating the input while sorting.** `list.sort()` changes the caller's list; `sorted()` makes a copy. Prefer `sorted` unless the problem allows mutation.
6. **No tie-breaker in a heap of trees.** In Huffman, `(weight, tree)` crashes on equal weights; use `(weight, counter, tree)`.
7. **Dividing by zero in ratio keys.** An item with weight 0 or a job with profit 0 breaks `a / b`. Handle it or use cross-multiplication.
8. **Floating-point ties.** Comparing `0.1 + 0.2` with `0.3` is unreliable; compare ratios as integer cross-products or `Fraction`s when exactness matters.
9. **Proving only one direction.** An exchange argument must show the swapped answer is *valid* (still feasible) and *no worse*. Missing the first half is a frequent hole.
10. **Using a greedy proof beyond its assumptions.** Dijkstra with a negative edge; fractional knapsack logic on lumps; canonical-coin reasoning on a random coin set.
11. **Off-by-one in array greedy.** Jump game II should loop to `len(nums) - 1`, not `len(nums)`, or it counts a jump that is not needed. Test on a one-element array.
12. **Calling it greedy when the real tool is a stack or two pointers.** Some "greedy" array tricks are really invariants of a stack (remove K digits). The name is not important; the invariant is.
13. **Edge cases.** Empty input, a single element, all-equal values, everything overlapping, nothing overlapping, and amounts or capacities of 0.

## 17. Summary

- A **greedy algorithm** makes the locally best choice at every step and never undoes it. It is short and fast, but only *sometimes* correct.
- It is correct when the **greedy-choice property** (some optimal answer contains the greedy choice) and **optimal substructure** (what remains is the same kind of problem) both hold.
- The two main proof tools are the **exchange argument** (rearrange an optimal answer into the greedy answer without making it worse) and the **stay-ahead argument** (greedy is never behind the optimal answer after any step). A **lower bound that greedy matches** is a third.
- The cheapest way to refute a greedy rule is a **small counterexample**, found by hand, by thinking about a tempting-but-wrong item, or by comparing against **brute force** on random tiny inputs.
- **Interval scheduling:** sort by **end time** and take what fits (`O(n log n)`). Related: minimum removals (`n - kept`), minimum arrows (sort by end, closed intervals), merge (sort by start, use `max`), minimum platforms / rooms (sweep, or a min-heap of end times). The weighted version is **not** greedy.
- **Fractional knapsack:** best density first (`O(n log n)`). **0/1 knapsack:** density greedy fails; use DP.
- **Coin change:** greedy is correct for *canonical* coin systems (usual money) and wrong for others (`1, 3, 4`). BFS or DP is the safe general tool. Only amounts below the sum of the two largest coins need checking.
- **Scheduling:** shortest job first for total waiting; `time / weight` for weighted completion; earliest deadline first for maximum lateness; profit order plus latest free slot (or a min-heap by deadline) for jobs with deadlines.
- **Array greedy:** assign cookies (sort and pointer), jump game (farthest reach), jump game II (layer ends), gas station (reset when negative), many-trade stock profit (sum of rises), lemonade change (spend the less flexible bill first).
- **Huffman coding:** repeatedly join the two lightest trees with a min-heap of `(weight, tie-breaker, tree)`. Prefix-free codes; `O(k log k)` for `k` distinct letters; the tie-breaker prevents comparing trees.
- **Matroid intuition:** if the feasible sets have the hereditary and exchange properties, "heaviest first, keep if feasible" is optimal. Kruskal and job sequencing are examples; knapsack is not.
- Greedy hides inside Kruskal, Prim and Dijkstra. Their proofs use the same ideas, and Dijkstra's proof breaks on negative edges.

### Complexity table

| Algorithm | Time | Extra space |
|---|---|---|
| Activity selection, minimum arrows, merge intervals | `O(n log n)` (sort) | `O(n)` |
| Minimum platforms (two sorted lists) | `O(n log n)` | `O(n)` |
| Minimum rooms (heap of ends) | `O(n log n)` | `O(n)` |
| Fractional knapsack | `O(n log n)` | `O(n)` |
| Greedy coin change (canonical) | `O(c log c)` for `c` coins | `O(1)` |
| Shortest job first, EDF, Smith's rule | `O(n log n)` | `O(n)` |
| Job sequencing, slot search / heap | `O(n^2)` / `O(n log n)` | `O(n)` |
| Assign cookies | `O(n log n + m log m)` | `O(1)` extra |
| Jump game I and II, gas station, stock profit | `O(n)` | `O(1)` |
| Huffman coding | `O(k log k)` after counting | `O(k)` |

### Self-check

- [ ] I can state the greedy-choice property and optimal substructure, and say what each means for a problem.
- [ ] I can write an exchange argument for activity selection and for shortest job first in my own words.
- [ ] I can explain the stay-ahead argument and use it to compare greedy with an optimal answer.
- [ ] I can find a counterexample to "earliest start", "shortest", density greedy on 0/1 knapsack, and greedy coin change on `(1, 3, 4)`.
- [ ] I can write activity selection, merge intervals, minimum arrows and minimum platforms without looking, and say whether touching intervals overlap in each.
- [ ] I can solve jump game I and II, gas station, assign cookies and stock profit in one pass each, and say what the state variable means.
- [ ] I can build Huffman codes with `heapq`, explain the tie-breaker, and encode and decode a short string.
- [ ] I can write a brute-force stress test to check a greedy idea.
- [ ] I can say, for a new problem, whether I expect greedy to work, and name the proof or the counterexample.

### How to practise

Do the problems in the order of the chapter: the tiny proofs and counterexamples first (they build the habit of testing), then interval problems, then knapsack and coin change, then scheduling, then the array problems, and last Huffman. **For every problem, write the greedy rule in one sentence before you code, and write the one-sentence reason it is safe.** If you cannot, test it against brute force before you trust it. When a greedy solution fails a hidden test, do not patch it; look for the missing case in the proof. The site problems for this module (LeetCode, CSES, Codeforces) will be listed for you in the module's external list.

### Further reading

- Thomas Cormen, Charles Leiserson, Ronald Rivest and Clifford Stein, *Introduction to Algorithms*, the chapter "Greedy Algorithms": activity selection, Huffman codes, and the section on matroids.
- Jon Kleinberg and Eva Tardos, *Algorithm Design*, chapter 4: the exchange argument and the stay-ahead argument, with scheduling problems.
- Robert Sedgewick and Kevin Wayne, *Algorithms*, section 5.5 ("Data Compression") for Huffman coding.
- Dexter Kozen and Shmuel Zaks, "Optimal bounds for the change-making problem" (1994), for the bound on testing coin systems.
- David Huffman, "A Method for the Construction of Minimum-Redundancy Codes" (1952).

Next module: **dsa.14 Dynamic programming**. Every time a greedy rule fails in this chapter (0/1 knapsack, general coin change, weighted intervals), dynamic programming is the technique that takes over.
