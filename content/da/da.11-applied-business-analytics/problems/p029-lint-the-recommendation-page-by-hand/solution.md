## Approach

- Headline has digits: no issue.
- Recommendation 1 has an owner and the date "28 February 2025" matches; recommendation 2 has an owner but "soon" does not match -> `recommendation 2 has no date`.
- Impact "about 40,000 rupees of contribution a month": only one number, and the word `to` does not occur as a separate word (`contribution` does not count) -> `impact is a point, not a range`.
- Evidence has three items; the third has no digit -> `evidence needs at least two items, each with a number`. The first item contains "CI", so the uncertainty check passes.
- Two limitations: fine. A next step contains "Success": fine.
- The text "look into" appears in the second limitation -> `vague phrase: 'look into'`.

Four issues.

## Code

```text
recommendation 2 has no date
impact is a point, not a range
evidence needs at least two items, each with a number
vague phrase: 'look into'
4
```

## Complexity

Not applicable (a trace problem).

## Another way

A human reviewer would also ask for a range in the impact, a date, and a real limitation (assumptions about margin and CAC) instead of "the data are synthetic": the linter catches form, not substance.
