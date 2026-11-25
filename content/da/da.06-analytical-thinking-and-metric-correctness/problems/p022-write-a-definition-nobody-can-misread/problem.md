# Write a definition nobody can misread

Chapter sections 7.1 to 7.4, 8.2 to 8.4. Two managers argue: one says February's completion rate is 89 percent, the other 98
percent. Both are using the phrase "monthly completion rate" for QuickFix.

In `answer.md`, in about 250 to 350 words, write the **definition** of "monthly completion rate" so that two analysts
working apart compute the same number. The definition must say, in sentences or a short list:

- the **numerator** and the **denominator**, and why the numerator is a subset of the denominator;
- the **date basis** (which timestamp puts a job in a month) and the **time zone**;
- how the month is cut (the exact start and end);
- which **statuses** are in the denominator and which are left out, and why;
- what happens to **jobs that are too recent** to have finished (immature jobs);
- the **owner** of the metric and its **version**.

Then add two or three lines: what the two managers probably did differently.

## Example

A start: "Monthly completion rate (v1, owner: operations): of the jobs created in the month, the share that is completed.
Numerator: jobs created in the month with status `completed`. Denominator: ..."
