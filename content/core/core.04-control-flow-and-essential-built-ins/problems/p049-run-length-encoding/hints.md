## Hint 1

Walk through the characters, keeping the **current** run's character and its count. What
should happen when the next character is different?

## Hint 2

When the character changes, the current run is finished: add it to the result and start a new
run with count 1.

## Hint 3

After the loop ends, the last run has not been added yet. Every "group" loop needs this final
step.
