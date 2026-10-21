# Average report with narrow try blocks

Write `average_report(marks_by_student)` where `marks_by_student` is a dict from a student's name
to a list of marks. Return a list of lines, **sorted by name**:

- `"<name>: <average with 1 decimal>"`, for example `"Asha: 78.5"`;
- `"<name>: no marks yet"` when the list is empty.

Compute the average as `sum(marks) / len(marks)` and handle the empty list by catching
`ZeroDivisionError`. Keep the `try` block **narrow**: it must contain only the one statement that
computes the average (section 13). Build the line in `else`.

If a list contains something that is not a number (for example the string `"80"`), `sum` raises
`TypeError`. That is bad data from the caller: let it propagate.

**Example**

```python
average_report({"Ravi": [70, 81], "Asha": [80, 77, 78.5], "Zoya": []})
# ['Asha: 78.5', 'Ravi: 75.5', 'Zoya: no marks yet']
```
