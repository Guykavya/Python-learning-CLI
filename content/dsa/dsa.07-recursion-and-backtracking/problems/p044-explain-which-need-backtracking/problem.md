# Explain: which problems need backtracking?

For each of the eight problems below, choose the tool that fits best (chapter section 17):

| Label | Tool |
|---|---|
| **B** | backtracking (search with choose / explore / un-choose, maybe pruning) |
| **D** | dynamic programming (memoised recursion or a table) |
| **G** | greedy (one safe local choice at every step) |
| **L** | a plain loop (one pass, maybe with a dictionary or set) |

1. List **every** way to place 8 rooks on an 8x8 board that has some forbidden squares, so that no two rooks share a row or column.
2. **Count** the ways to climb a staircase of 1,000 steps taking 1 or 2 steps at a time (answer modulo `10**9 + 7`).
3. Find the **largest** number in a list of 100,000 numbers.
4. Pay an amount with the **fewest** coins when the coins are 1, 2, 5, 10, 20, 50, 100, 200 (euro cents).
5. Fill a crossword grid with words from a 500-word list so that all crossings agree.
6. **Count** the subsets of 100 numbers (each between 1 and 100) whose sum is 2,500.
7. **Generate** every string of `n = 4` pairs of balanced brackets.
8. Check whether a string of 100,000 characters has two equal adjacent characters.

In `answer.md`, write eight lines `1: X`. Then pick **one** problem labelled B and **one** labelled D and justify each in two sentences, using the words *state*, *repeated*, and the **size** of the input.
