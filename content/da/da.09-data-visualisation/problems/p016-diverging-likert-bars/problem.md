# Diverging Likert bars

Chapter section 4.6. A survey answer on a five-point scale has a neutral centre. A **diverging stacked bar** puts the disagreeing answers to the
**left** of zero, the agreeing answers to the **right**, and **splits the neutral answers half and half** across zero, so the eye compares the two sides.

Write `likert_bars(counts)`. `counts` is a DataFrame: one row per question (the index), five columns in this order:
`Strongly disagree, Disagree, Neutral, Agree, Strongly agree`, holding **counts**.

- turn each row into percentages of its total;
- draw **one `ax.barh` call per category** (five calls, in the column order), each with one bar per question, using the `left=` argument;
- for one question with percentages `sd, d, n, a, sa` (and `half = n / 2`) the left edges are
  `-(sd + d + half)`, `-(d + half)`, `-half`, `half`, `half + a` and the widths are the percentages themselves;
- a category with 0 percent still draws a **zero-width bar** (do not skip it);
- draw a vertical line at 0, label the x axis `Share of answers (%)`, and add a legend with the five column names.

So `ax.patches[c * n_questions + q]` is category `c` of question `q`.

## Example

A question with counts `10, 20, 20, 30, 20` (total 100) has left edges `-40, -30, -10, 10, 40` and widths `10, 20, 20, 30, 20`.
