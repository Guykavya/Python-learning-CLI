## Hint 1

Go through the five checks for each finding, in the order of the code. `\b(from|to|than|vs)\b` needs one of those **whole words**; `\d{4}-\d{2}-\d{2}` needs a date written like `2025-01-31`.

## Hint 2

Finding 3: does "Churn rose by 1.7 points" contain the word `to`? Is "31 January 2025" in the form `dddd-dd-dd`? How many limitations does it have?
