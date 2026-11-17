## Approach

Follow the loop with a table: the clock, the waiting jobs (sorted tuples) and the job that runs. A job joins the waiting set as soon as `arrival <= time`. The smallest tuple `(duration, arrival, job)` runs next; its wait is `time - arrival`.

## Trace

```text
time  arrived and waiting (before the pick)             picked             waited  clock after
0     (6,0,0)                                           job 0 (6)          0       6
6     (3,1,1) (3,2,2) (1,3,3)                           job 3 (1)          3       7
7     (3,1,1) (3,2,2)                                   job 1 (3)          6       10
10    (3,2,2)                                           job 2 (3)          8       13
13    nothing, next arrival at 20 -> idle               (jump to 20)
20    (2,20,4)                                          job 4 (2)          0       22
```

Total wait: `0 + 3 + 6 + 8 + 0 = 17`, average `17 / 5 = 3.4`.

## Answers to the questions

1. At time 6 the jobs 1, 2 and 3 are all waiting, and job 3 has the shortest duration (1), so it runs first although it arrived last. In first come, first served the order would be jobs 0, 1, 2, 3 (then 4): waits `0, 5, 7, 9` and `0` for job 4: total 21, average `4.2`. Shortest job first gives `3.4`: short jobs do not wait behind long ones.
2. The duration is equal (3), so the second field decides: the arrival. Job 1 (arrived at 1) runs before job 2 (arrived at 2). You see it in the lines `t=7` and `t=10`, and in the order of the tuples in the `still waiting` list at `t=6`.
3. The `idle` line is printed at the start of a round, when the heap is empty **and** the next job has not arrived. After job 2 finishes the clock is 13, the heap is empty and job 4 arrives at 20: the processor waits from 13 to 20.

## Another way

Compare with the O(n^2) version of the chapter, which scans all arrived jobs for the minimum at each decision: it makes the same choices, but a heap picks the shortest job in `O(log n)`.
