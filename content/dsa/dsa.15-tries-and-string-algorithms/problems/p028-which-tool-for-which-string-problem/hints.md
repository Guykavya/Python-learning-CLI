## Hint 1

Ask first: is it a **plain search, asked once**? Then the built-ins win. Only when the built-ins cannot do the job does a special tool earn its place (chapter section 16): many queries, a stream, many patterns, periods and borders, palindromes, or matches at every position.

## Hint 2

Look for the key phrase in each task: "start with the letters typed" (prefixes), "one at a time, without storing" (stream), "repeated block" (period), "many words of the same length" (fingerprints), "palindromic" (centres), "at every position, how many leading letters" (prefix matches starting at `i`), "occurs twice, longest" (monotone length).

## Hint 3

For the two explanations, count how many times each tool reads the text, and which question its table answers: "ending at `i`" (prefix function) or "starting at `i`" (Z).
