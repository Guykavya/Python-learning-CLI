## Hint 1

Does any line print before the error appears? What does that tell you about
when Python checks the grammar?

## Hint 2

The error message names the problem: a bracket that was "never closed", or a
string literal that is "unterminated" (has no closing quote). A string must
open and close with the *same* kind of quote.

## Hint 3

Each line needs: `print(` + an opening quote + the text + the *same* closing
quote + `)`.
