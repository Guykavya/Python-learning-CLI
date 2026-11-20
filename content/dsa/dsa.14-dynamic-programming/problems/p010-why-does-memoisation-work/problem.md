# Explain: why does memoisation work?

Chapter section 1 shows that `fib(25)` makes 242,785 calls without a notebook and 49 with one. Problem p002 counted 25 calls against 11 for `fib(6)`. A notebook is a tiny change to the code. Why does it change the running time from exponential to linear, and why does the same trick do **nothing** for some other recursions?

Write a short explanation (8 to 14 sentences) in `answer.md`. Answer these questions:

1. In the call tree of `fib(6)` without a notebook, which calls are **repeated**? Name two, and say how many times each is made.
2. What are the two properties a problem needs for DP (chapter section 1)? Which one is the reason a notebook helps?
3. Why does a notebook make the number of real computations equal to the number of **distinct states**? State the running-time formula from chapter section 2 and apply it to `fib(n)`.
4. The backtracking function below lists all orderings of a list. Would adding `@functools.cache` to `perms` make it faster? Why not?

   ```python
   def perms(chosen, remaining):        # chosen and remaining are tuples
       if not remaining:
           return [chosen]
       result = []
       for i in range(len(remaining)):
           result += perms(chosen + (remaining[i],), remaining[:i] + remaining[i + 1:])
       return result
   ```

5. Chapter section 3 shows `count_ways(coins, amount, memo={})` returning 3 instead of 1 for coins `[1, 5]`. Explain the rule about the memo key that this breaks. What must the key contain?

## Example of the level of detail wanted

For question 1, a good sentence is: "`fib(3)` is computed 3 times and `fib(2)` 5 times, once for every path in the tree that leads to it; each of these computations does exactly the same work." Name the calls and the counts; do not only say "it saves time".

Then compare with the model answer and rate yourself.
