# Explain: what is a stable sort?

Look at these records, sorted by **age** only:

```python
people = [("ann", 30), ("bob", 25), ("cy", 30), ("dee", 25)]
print(sorted(people, key=lambda p: p[1]))
```

Answer in `answer.md`, in your own words (150 to 300 words):

1. **Definition.** What does it mean that a sort is *stable*? Which two records in the example does it concern?
2. **The output.** What does the example print if the sort is stable? What could it print if the sort is *not* stable?
3. **Why it matters.** Give one real situation where stability is needed (think of sorting a table by two columns one after the other).
4. **Recipe.** How do you sort by `age` ascending and, within the same age, by `name` ascending using two stable sorts? In which order do you run them, and why?
5. **Which of the sorts in this chapter are stable?** Name two that are and two that are not (or are not by default).

Then read `solution.md` and `answer.md`, and rate your answer.
