# Name the leak family

Chapter section 2. Leaks come in four families: **preprocessing** (something was fitted on all rows), **target** (a column is a consequence of the outcome), **duplicates/groups** (the same entity on both sides of the split) and **time** (information from after the prediction moment). A quick keyword rule sorts stories:

```python
def family(story):
    s = story.lower()
    if "after" in s or "future" in s or "next" in s:
        return "time"
    if "same patient" in s or "duplicate" in s or "twice" in s or "same customer" in s:
        return "duplicates/groups"
    if "scaled" in s or "selected" in s or "imputed" in s or "whole data" in s:
        return "preprocessing"
    if "outcome" in s or "written by" in s or "refund" in s:
        return "target"
    return "unknown"


stories = [
    "Features were scaled on the whole data before the split",
    "A refund flag is filled in when the customer complains",
    "The same patient appears in train and test",
    "Rolling averages include the next day's sales",
    "Rows were loaded twice by the import job",
    "Missing values were imputed with the mean of all rows",
    "The diagnosis code is written by the doctor after the outcome",
    "Top 20 features were selected using the test labels",
]
for i, story in enumerate(stories, start=1):
    print(f"{i}: {family(story)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For the single story `"The model saw the future prices"` the program would print `1: time`.

## After you answer

- Story 7 is printed as one family but belongs more naturally to another. Which, and why did the rule get it wrong?
