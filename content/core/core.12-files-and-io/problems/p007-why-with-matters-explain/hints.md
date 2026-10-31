## Hint 1

Writing to a disk for every single `write()` call would be slow. What does Python do instead, and when does it finally hand the data to the operating system?

## Hint 2

Answer in order: (1) the buffer in memory, (2) what is lost on a crash, (3) `close()` flushes, and `with` calls it even on errors, (4) limits on open files, locked files, (5) the code.
