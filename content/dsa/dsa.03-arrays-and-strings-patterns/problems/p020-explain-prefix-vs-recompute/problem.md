# Explain: prefix sums versus re-adding

An array has `n` numbers and you must answer `q` questions "what is the sum of positions `l..r`?". Two programs:

```python
# Program A: re-add every range
for l, r in questions:
    print(sum(a[l - 1:r]))
```

```python
# Program B: prefix sums
p = [0]
for x in a:
    p.append(p[-1] + x)
for l, r in questions:
    print(p[r] - p[l - 1])
```

Answer in `answer.md`, in your own words, with small numbers where they help. Aim for 150 to 300 words.

1. **Cost of A.** In the worst case, how many additions does Program A do for `n = q = 200000`? Which questions are the
   worst ones?
2. **Cost of B.** How much work does B do before the first question, and how much per question? Give the total as a
   formula in `n` and `q`, and as a number for `n = q = 200000`.
3. **Why it works.** Explain in one or two sentences why `p[r] - p[l - 1]` is exactly the sum of positions `l..r`, and
   why `p` starts with a 0.
4. **What it costs.** What extra memory does B use? When is A the better choice anyway?
5. **A limit.** Suppose that between questions, single elements of `a` can change. What happens to Program B's
   speed, and why?

Then read `solution.md` and `answer.md`, and rate your answer.
