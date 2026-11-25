# The criteria language by hand

Chapter section 6.2. The criteria of `COUNTIF`, `COUNTIFS`, `SUMIFS` and `AVERAGEIFS` are written as **text** with their own rules:

- a bare word matches text **case-insensitively and exactly** (`"north"` matches `North`, not `North ` with a space);
- `"<>word"` matches **everything else**, including blank cells and numbers;
- `"*"` stands for any characters, `"?"` for one character: `"N*"` matches text starting with N;
- `">=10"` compares **numbers only**: text never satisfies a number test;
- `"<>"` (nothing after) matches every cell that is **not empty**; `"="` matches **only empty cells**.

Column `A`, rows 1 to 8, holds:

| row | A |
|---|---|
| 1 | North |
| 2 | north |
| 3 | South |
| 4 | *(empty cell)* |
| 5 | 12 |
| 6 | 8 |
| 7 | Nord |
| 8 | N/A |

The formulas `=COUNTIFS(A1:A8, criterion)` are evaluated for these six criteria, in this order: `">=10"`, `"<>North"`, `"N*"`, `"north"`, `"<>"`, `"="`.

Work out the count each formula gives and write **the six numbers, one per line, in this order**, in `answer.txt`. (The numbers are what the chapter's evaluator MiniXL gives; Excel agrees.)

## Example

For the criterion `"South"` the count would be `1`.

## After you answer

- Why does `"<>North"` count 6 and not 5?
- Which two criteria count the same cells as "everything" minus "nothing"?
