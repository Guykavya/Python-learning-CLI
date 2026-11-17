## Hint 1

Do not simulate the heap array. Keep the waiting jobs as a set of tuples `(duration, arrival, job number)` and write it **sorted**, because the program prints it sorted. At time 0 only job 0 has arrived. It runs for 6 units: where is the clock when it finishes, and which jobs have arrived by then?

## Hint 2

At time 6 the waiting jobs are 1, 2 and 3: `(3, 1, 1)`, `(3, 2, 2)` and `(1, 3, 3)`. The smallest tuple is compared field by field: first the duration. Which job is it? Write the line, remove its tuple, and move the clock. Tuples with an equal first field are decided by the second field.

## Hint 3

Worked start:

```text
t=0: run job 0 (duration 6), waited 0, still waiting []
t=6: run job 3 (duration 1), waited 3, still waiting [(3, 1, 1), (3, 2, 2)]
```

Continue at `t=7`. After the last waiting job has run, the heap is empty. Is the next job (job 4, arrival 20) there already? Then which `if` in the code fires, and what does it print?
