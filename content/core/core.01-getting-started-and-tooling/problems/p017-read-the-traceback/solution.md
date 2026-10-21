## Walkthrough

1. The file compiles fine: every line is valid grammar. So it starts running.
2. Lines 1 to 4 run. Lines 3 and 4 print `Student: Riya` and `Marks: 87`.
   (`print` puts a space between its values and converts 87 to text itself.)
3. Line 5: `"Total: " + marks` asks `+` to join a `str` with an `int`. Python
   refuses to guess and raises `TypeError`.
4. Lines 6 and 7 never run.

The real output:

```
Student: Riya
Marks: 87
Traceback (most recent call last):
  File "/home/asha/report.py", line 5, in <module>
    message = "Total: " + marks
              ~~~~~~~~~~^~~~~~~
TypeError: can only concatenate str (not "int") to str
```

## The fix

`message = "Total: " + str(marks)`, or `print("Total:", marks)`.

## Lesson

Output printed before a traceback tells you how far the program got. The
`line N` in the last `File` entry tells you where it stopped.
