# Explain: DP, greedy or backtracking?

Chapter section 22 compares the three tools. For each task below, decide which one you would use: **greedy** (dsa.13), **dynamic programming** (this module) or **backtracking** (dsa.07). Pick the tool that is correct **and** fast enough for the sizes given; if two tools would both work, name the simpler one and say why.

1. Fewest coins to pay an amount up to 10**6 with the coins `[1, 5, 10, 25]`.
2. Fewest coins to pay an amount up to 10**4 with the coins `[1, 3, 4]`.
3. Print **every** way to place 8 queens on a chess board so that no two attack each other.
4. The largest number of meetings, from 10**5 meetings with start and end times, that one room can hold without overlaps.
5. The best total value from 100 items with weights up to 100, value given, a bag of capacity 10**4, each item taken whole or not at all.
6. The same 100 items, but you may take **any fraction** of an item (half a sack of rice is half its value).
7. The length of the longest common subsequence of two strings of 1,000 letters.
8. Print **every** subset of 15 given numbers whose sum is 30. (And a twin question: what if you only need **how many** such subsets there are, for 300 numbers?)

Write your answer in `answer.md`:

- For **all eight** tasks: one line with your choice and a short reason (5 to 15 words).
- For **two** tasks of your choice, one of them task 2 or task 6: a full justification (3 to 5 sentences). For a greedy choice, say what the greedy rule is and why it is safe, or give a counterexample that shows it is not. For DP, name the state and say why sub-problems repeat. For backtracking, say why nothing smaller than "the whole history" can be the state.

## Example of the level of detail wanted

For task 1, a good line is: "Greedy (largest coin first): US coins are a 'canonical' system, so greedy is always optimal; DP also works but needs a 10**6 table." Not: "Greedy, because it is fast."

Then compare with the model answer and rate yourself.
