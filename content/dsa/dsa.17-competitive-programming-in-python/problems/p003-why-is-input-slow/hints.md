## Hint 1

Think of the cost of one call (looking up `input`, checking whether `sys.stdin` and `sys.stdout` are terminals, flushing output, building a new string, stripping the newline). Multiply by 200 000.

## Hint 2

The operating system already gives the data in big chunks (buffer). What changes between `input()`, `sys.stdin.readline()` and `sys.stdin.read()` is how much Python-level work happens **per line**.

## Hint 3

Structure of a good answer: per-call overhead, repeated n times; buffering means the data is already in memory; `read()` does one call and the splitting happens in C; for n = 10 nobody notices; an interactive problem forces line by line.
