## Hint 1

Start with the number part alone: a digit, then digits or commas, then an optional `.` with
digits. Why must the decimal part be `(?:\.\d+)?` and not `\.?\d*`? (Think of `Rs.40.` at the
end of a sentence.) Why is the group non-capturing?

## Hint 2

Each lookbehind must have one fixed width, but you can put **several lookbehinds** side by side
as alternatives: `(?:(?<=A)|(?<=BB))`. Each alternative is fixed width on its own. How many do
you need for the four markers?

## Hint 3

```
NUMBER = \d[\d,]*(?:\.\d+)?
BEFORE = (?:(?<=₹)|(?<=₹ )|(?<=Rs\.)|(?<=Rs\. ))
for each s in findall(BEFORE + NUMBER, text):
    append float(s with "," removed)
```
