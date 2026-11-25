# Outlier or best customer?

Chapter sections 6.1, 6.4 and 6.5. A rule can only **point at suspects**; a person with domain knowledge decides. Three
suspects turned up in three different tables. For each one, decide what to do, and say why, in `answer.md`
(about 200 to 300 words in total).

1. **A shop's order table.** The median order is Rs 1,800. One order is Rs 9,00,000. The statistical rules flag it.
   The same customer placed 40 orders in the last year.
2. **A survey.** One respondent has `age = 140`. The questionnaire allowed ages 18 to 75.
3. **A sensor table.** A temperature sensor reports exactly 24.3 degrees for 8 hours in a row. The room is a normal
   office with an air conditioner, and the neighbouring sensors changed during those hours.

For each suspect answer: **Is it an error or a real value? What do you do with it (keep, fix, set to missing, flag,
remove)? What do you check first? What do you write in the report?**

Finish with one sentence on why you never just delete an outlier "because the rule said so".

## Example

A start: "A suspect is a question, not a verdict. For the Rs 9,00,000 order I would first ask whether this customer is a
company buying in bulk. If yes, it is a different population and I would keep it but analyse it separately..."
