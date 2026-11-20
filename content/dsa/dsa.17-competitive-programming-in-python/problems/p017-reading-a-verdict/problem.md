# Reading a verdict

A judge tells you very little: a verdict and a test number. Your skill is to guess the **most likely cause**. For each of the six reports below, choose one cause from the list (chapter section 14).

**Causes**

| Letter | Cause |
|---|---|
| A | The idea or formula is wrong, or the statement was misread (the sample already fails) |
| B | A special case: smallest input, equal values, zeros (`n = 1`, all equal, empty answer) |
| C | The algorithm or the input/output is too slow |
| D | Unbounded recursion (a very deep recursion in a recursive solution) |
| E | Too much memory: a huge table or a big copy |
| F | Output format: the number is right but the text is not (decimals, case, spacing) |

**Reports**

1. *Wrong answer on test 1.* Your output is `3`, the expected output is `3.00`. Your logic matches the jury's.
2. *Wrong answer on test 2.* Test 2 is `n = 1`, and your program prints `0` where the jury prints `5`.
3. *Time limit exceeded on test 17.* `n = 2 * 10**5`, your solution has two nested loops over the array.
4. *Runtime error on test 12.* The traceback ends with `RecursionError: maximum recursion depth exceeded`. Test 12 is a path with 10^5 vertices.
5. *Memory limit exceeded on test 8.* You build a table with `n` rows and `n` columns of integers, and `n = 5000`.
6. *Wrong answer on test 1.* The sample says `10`, your program prints `12`. You count each pair `(i, j)` and also `(j, i)`.

Write your answer in `answer.txt`, one line per report: `1: F`, `2: B`, and so on (your own letters).

## After you answer

1. For report 1 and report 6 the verdict is the same ("wrong answer on test 1"). What tells you which of A and F it is?
2. What would you try **first** for each report?
3. Which of the six could you have found with the stress test of chapter section 13, and which only by reading the statement again?
