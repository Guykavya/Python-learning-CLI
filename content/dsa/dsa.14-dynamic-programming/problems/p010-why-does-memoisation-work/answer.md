## Model answer

**1. Repeated calls.** In the tree of `fib(6)`, `fib(5)` is called once, `fib(4)` twice, `fib(3)` 3 times, `fib(2)` 5 times, `fib(1)` 8 times and `fib(0)` 5 times: 25 calls in all, but only 7 different questions (`fib(0)` to `fib(6)`). Every repeated call is the **same state** and returns the same answer by doing exactly the same work again.

**2. Two properties.** A problem fits DP when it has **overlapping sub-problems** (the same smaller question is asked many times along different paths) and **optimal substructure** (the big answer is built from the answers to smaller questions). Overlapping sub-problems is the reason the notebook helps: there must be repeats for remembering to save anything. Optimal substructure is what lets us write the recursion in the first place.

**3. Distinct states.** With a notebook, the first call for a state does the work and stores the answer; every later call for the same state finds it and returns at once. So the body does real work only once per distinct state; the repeated calls cost `O(1)` each. Time = (number of states) x (work per transition). For `fib(n)`: `n + 1` states, `O(1)` work each (one addition), so `O(n)` instead of about `1.6**n`. That matches the counts: `2n - 1` calls (49 for `n = 25`), `n + 1` of them doing work.

**4. Permutations.** Caching `perms` does not help, because its states never repeat. Each call has a different `chosen` prefix, so no two calls share the same arguments: there are no **overlapping** sub-problems, the cache only ever misses, and it costs extra memory. The output itself has `n!` lists, so no trick can make it polynomial. This is backtracking territory (dsa.07): every sub-problem is new.

**5. The memo key.** The key must identify the state completely: it must contain **everything the answer depends on** and nothing it does not. `(len(coins), amount)` drops the coin values, so `[1, 2]` and `[1, 5]` get the **same key** and the second call reads the stale answer of the first. On top of that, the default dictionary `memo={}` is created once and shared between calls with different inputs. The fixes: a key with the real state (the coins themselves as a tuple, or an index into one fixed list), and a fresh memo per top-level call (a closure, chapter section 3).

**Checklist: your answer should mention**
- [ ] concrete **repeated** calls with counts (for example `fib(3)` 3 times, `fib(2)` 5 times)
- [ ] the two properties: **overlapping** sub-problems and optimal substructure
- [ ] overlapping sub-problems is what the notebook exploits
- [ ] a repeated call is the **same state**, so it has the same answer
- [ ] work happens once per distinct state; later calls are `O(1)` lookups
- [ ] time = states x work per transition; `fib(n)` becomes `O(n)`
- [ ] `perms` has no repeated states (every prefix differs), so a cache never hits
- [ ] the memo key must contain everything the answer depends on; a shared default dict leaks between inputs
