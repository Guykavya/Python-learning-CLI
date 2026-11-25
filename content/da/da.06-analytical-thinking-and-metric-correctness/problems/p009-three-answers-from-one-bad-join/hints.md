## Hint 1

Which of the three numbers is a property of the **job**, and which of the **line**? For a job-level number, what must you
do to the table before summing? For the item count, what is special about the row of a job with no lines?

## Hint 2

```text
jobs      = number of distinct job_id
job_value = sum of quote_total after keeping one row per job_id
items     = count of line_no (count skips missing values, len does not)
return the three as ints
```
