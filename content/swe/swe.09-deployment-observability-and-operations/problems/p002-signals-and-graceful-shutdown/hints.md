## Hint 1

Make a table with the four signals as rows and "what Gunicorn does" as the column. Then ask which row is different: for which signal does the operating system, not your program, do the work?

## Hint 2

For part 2, think of `docker stop` as a polite request followed by a deadline. What happens at the deadline? For part 4, ask who is process number 1 in a container started with `CMD gunicorn ...`, and whether that process passes signals on.
