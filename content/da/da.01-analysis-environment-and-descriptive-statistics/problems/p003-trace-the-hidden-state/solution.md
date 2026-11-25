## Approach

Follow the run order, not the page order. The namespace after each run is the whole story: a variable only changes when the cell that assigns it is run again. The stale line is the print after `price = 80` that still shows `total 150`. The restart shows that a notebook that looked fine depended on an order nobody wrote down; run top to bottom the notebook gives `total is 240`.

## Code

The expected output is in `expected.txt`, produced by actually running the program above.

## Complexity

Eight runs, one namespace: nothing to optimise. The lesson is about state, not speed.

## Another way

Use `Restart and Run All` (the habit of Ch. 3.3) before trusting a notebook, or move the logic into functions that take inputs instead of reading global names.
