## Hint 1

Keep a list of runs, where each run is `[token, count]`. When does a new run start?

## Hint 2

For each token: if the list is not empty and `runs[-1][0] == token`, add 1 to `runs[-1][1]`;
otherwise append `[token, 1]`.

## Hint 3

Build each output piece as `t if n == 1 else f"{t}*{n}"`.
