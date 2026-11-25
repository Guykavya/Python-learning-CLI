# MCAR, MAR, MNAR

Chapter section 8.1 to 8.4. Explain in `answer.md` (about 300 words) the three ways a value can go missing. Use the
survey of the chapter (columns `age`, `city`, `income`, `satisfaction`, `phone`):

1. Define **MCAR**, **MAR** and **MNAR** in one sentence each. The key question in every sentence is: *what does the
   chance of being missing depend on?*
2. Give **one example of each from the survey** (for instance, which column goes missing and why).
3. For each mechanism, say what happens to the **complete-case mean** of `income` (the mean of the people who
   answered): unbiased, biased in which direction, and can it be repaired using the other columns?
4. Can you tell the three apart **from the data alone**? What can you check, and what can you not?

## Example

A start: "In all three cases some incomes are missing. What differs is *why*. If the reason is a pure accident that has
nothing to do with the person or the income, the data is missing completely at random (MCAR)..."
