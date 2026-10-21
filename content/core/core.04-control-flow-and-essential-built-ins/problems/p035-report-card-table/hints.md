## Hint 1

Which built-in gives row numbers from 1? Which walks two lines together?

## Hint 2

`for n, (subject, mark) in enumerate(zip(subjects, marks), start=1):`

## Hint 3

`all(int(m) >= 40 for m in marks)` answers the overall question. What does `all` give for no
marks at all?
