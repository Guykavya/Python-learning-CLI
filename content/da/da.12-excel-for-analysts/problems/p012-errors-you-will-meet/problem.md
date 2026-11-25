# Errors you will meet

Chapter section 6.5. An Excel error value (`#DIV/0!`, `#N/A`, ...) **spreads**: a formula that uses a cell with an error gets an error too, unless a function catches it. `IFERROR` catches **every** error; `IFNA` catches **only** `#N/A`.

Sheet `S` holds, in `A1:B4`, the keys `a, b, c, d` and the numbers `1, 2, 3, 4`; the cell `B5` is **empty**. These five formulas are in `F1` to `F5`:

| cell | formula |
|---|---|
| F1 | `=B1/B5` |
| F2 | `=XLOOKUP("z",A1:A4,B1:B4)` |
| F3 | `=IFERROR(XLOOKUP("z",A1:A4,B1:B4),0)` |
| F4 | `=IFNA(B1/B5,"n/a")` |
| F5 | `=SUM(D1:D3)` (and `D1` holds `=XLOOKUP("z",A1:A4,B1:B4)`, `D2` and `D3` are empty) |

Write what each of the cells **F1 to F5 shows**, one per line, in order, in `answer.txt`, exactly as Excel displays it (a whole number without decimals, errors with their code).

## Example

`=1/0` in a cell shows `#DIV/0!`; `=IFERROR(1/0,5)` shows `5`.

## After you answer

- Why is `IFERROR(..., 0)` dangerous in a revenue report?
- Which of the five uses a function that does **not** catch the error it meets?
