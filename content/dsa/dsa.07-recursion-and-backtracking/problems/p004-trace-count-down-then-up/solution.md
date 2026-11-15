## Approach

Follow the call stack. On the way down every call prints `down n` before calling. The deepest call `show(0)` prints `base` and returns. Then each waiting call resumes and prints `up n`, innermost first.

## Expected output

```text
down 3
down 2
down 1
base
up 1
up 2
up 3
done
```

## Why

```text
show(3): down 3 -> show(2): down 2 -> show(1): down 1 -> show(0): base
                                     show(1) resumes: up 1
                    show(2) resumes: up 2
show(3) resumes: up 3
```

`show(n)` prints `2n + 1` lines, so `show(10)` prints 21 lines, plus the final `done`.
