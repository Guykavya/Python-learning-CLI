# Explain: why insertion sort loves nearly sorted data

Insertion sort takes `n^2 / 2` steps on a random list, but about `n` steps on a list that is already sorted, or sorted except for a few
elements that are slightly out of place. Answer in `answer.md`, in your own words, with small examples. Aim for 150 to 300 words.

1. **Cost formula.** Roughly how many shifts does insertion sort do, in terms of the number of inversions `I`? What is the total running time in terms of `n` and `I`?
2. **Sorted input.** How many shifts for `[1, 2, 3, 4, 5]`? Why?
3. **Nearly sorted.** Give a list of 10 numbers with `I = 2`. How many steps does insertion sort need?
4. **Reverse input.** What is `I` for a list of `n` numbers in decreasing order? Why is that the worst case?
5. **Practical use.** Why do fast library sorts (Timsort, introsort) still use insertion sort on tiny pieces?

Then read `solution.md` and `answer.md`, and rate your answer.
