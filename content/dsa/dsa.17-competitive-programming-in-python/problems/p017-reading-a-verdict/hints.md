## Hint 1

Read each report as a sentence: the verdict names the *kind* of failure, the details say *where*. A runtime error with `RecursionError` names its cause directly.

## Hint 2

Reports 1 and 6 both fail the very first test. Report 1 says the numbers match in value (`3` vs `3.00`); report 6 says the value itself is different (`12` vs `10`) and gives the reason.

## Hint 3

Match by symptom: format of the number gives F; smallest input gives B; nested loops over `2 * 10**5` gives C; `RecursionError` gives D; `n * n` table with `n = 5000` gives E; pairs counted twice gives A.
