## Hint 1

Take `03/04/2024`. Write down two sentences: "In a day-first country this is ...", "In a month-first country this is ...". Does either reading cause an error? What does that mean for finding the mistake later?

## Hint 2

```text
1. ambiguous -> valid in both orders -> no error; mixed rows with day > 12 -> error
2. clues in the data: a number above 12 in the first or the second position
   clue outside: who exported it, which country, which program
3. write format="%d/%m/%Y" explicitly; errors="coerce"; count the NaT you created; check min and max date
```
