# Answer first

Chapter sections 1.3 and 6.1. A headline is one sentence with **what changed**, **from what to what**, **when** and **why**. A reader who stops after it
should know the answer.

Write `headline(metric, before, after, period, cause="", unit="%")` that builds that sentence from numbers, so that it is never typed by hand:

- the verb is `rose` when `after` is larger than `before`, `fell` when it is smaller, both compared **after rounding to one decimal**;
  then the sentence is `"{metric} rose from {before}{unit} to {after}{unit} in {period}"` with both numbers written with one decimal;
- when the two rounded values are equal, the sentence is `"{metric} stayed at {before}{unit} in {period}"`;
- when `cause` is not empty, add `", mainly because {cause}"` at the end;
- a headline must be short: if it has **more than 40 words** (split on spaces), raise `ValueError` with the text `headline is N words (more than 40)`.

## Example

```python
headline("Monthly churn", 4.04, 5.68, "Sep-Dec 2024", "late deliveries more than doubled")
# 'Monthly churn rose from 4.0% to 5.7% in Sep-Dec 2024, mainly because late deliveries more than doubled'
```
