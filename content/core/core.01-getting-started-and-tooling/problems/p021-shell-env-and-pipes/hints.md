## Hint 1

What is in the `demo` folder when `ls` runs? `ls` piped into `wc -l` prints one
name per line. Which lines of `fruits.txt` contain the letters `an` next to
each other?

## Hint 2

A shell variable created with `NAME=value` is visible to `echo $NAME` in the
same shell, but is **not** copied to child programs until it is exported.

## Hint 3

`LEVEL=pro command` sets `LEVEL` only in the environment of that one command.
The shell itself keeps no `LEVEL`. And `>` replaces the whole file.
