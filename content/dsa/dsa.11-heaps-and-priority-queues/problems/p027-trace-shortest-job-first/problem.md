# Trace: shortest job first

This is the shortest-job-first scheduler of chapter section 10, with a `print` for every decision. A processor runs one job at a time and never stops a job that has started. When it is free, it takes, among the jobs that have **already arrived**, the one with the **shortest duration**; on a tie in duration it takes the job that arrived earlier, and if that is a tie too, the job with the smaller number (its position in the input list). Predict **exactly** what the program prints. Do not run it.

```python
import heapq

def sjf(jobs):
    order = sorted(range(len(jobs)), key=lambda i: jobs[i][0])     # job numbers, earliest arrival first
    heap, nxt, time, total_wait = [], 0, 0, 0
    for _ in range(len(jobs)):
        if not heap and time < jobs[order[nxt]][0]:
            print(f"t={time}: idle until {jobs[order[nxt]][0]}")
            time = jobs[order[nxt]][0]
        while nxt < len(order) and jobs[order[nxt]][0] <= time:
            i = order[nxt]
            heapq.heappush(heap, (jobs[i][1], jobs[i][0], i))      # shortest duration, then earlier arrival, then job number
            nxt += 1
        duration, arrival, i = heapq.heappop(heap)
        wait = time - arrival
        total_wait += wait
        print(f"t={time}: run job {i} (duration {duration}), waited {wait}, still waiting {sorted(heap)}")
        time += duration
    print(f"average wait {total_wait / len(jobs)}")

sjf([(0, 6), (1, 3), (2, 3), (3, 1), (20, 2)])
```

The jobs are `(arrival, duration)`, so job 0 arrives at time 0 and lasts 6, job 1 arrives at time 1 and lasts 3, and so on.

Write your answer in `answer.txt`, one printed line per line (seven lines). Copy the format of the `print` calls exactly. `still waiting` shows the heap after the chosen job was taken out, as a **sorted** list of tuples `(duration, arrival, job number)`; an empty heap prints `[]`. A job's `waited` is the time from its arrival until it starts. The last line is the average, as `print` writes a float.

## How to work

Keep four things on paper: the clock `time`, the list of jobs that have arrived and are waiting (the heap, as sorted tuples), the next job to arrive, and `total_wait`. In every round of the loop:

1. if nothing is waiting and the next job has not arrived yet, the processor is idle: one `idle` line, and the clock jumps;
2. every job with `arrival <= time` enters the heap (note the `<=`);
3. the smallest tuple leaves the heap and runs; print the line, then move the clock by its duration.

## After you answer

1. Job 3 arrives later than jobs 1 and 2 but runs before them. Why? Would it run first in "first come, first served"? What would the average wait be then (work it out)?
2. Jobs 1 and 2 have the same duration. Which tuple field decides, and in which line can you see the effect?
3. Why is the line `idle until 20` printed after the third job has finished and not earlier?
