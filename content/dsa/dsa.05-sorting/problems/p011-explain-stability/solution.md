## Approach

Look at records whose keys are equal. A stable sort keeps their input order.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- Definition mentions equal keys keeping input order.
- The expected stable output is given.
- A two-pass example (sort by name, then by age) is explained.
- Merge sort, insertion sort, bubble sort, counting sort (done right) and Python's Timsort are stable; selection sort, heap sort and the usual quicksort are not.
