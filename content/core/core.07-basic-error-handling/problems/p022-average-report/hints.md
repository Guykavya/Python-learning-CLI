## Hint 1

Which single line raises `ZeroDivisionError` for an empty list? Only that line goes in `try`.

## Hint 2

```
for name in sorted(...):
    marks = ...
    try:
        average = sum(marks) / len(marks)
    except ZeroDivisionError:
        append the "no marks yet" line
    else:
        append the formatted line
```
