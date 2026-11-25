# Correlation is not causation

Chapter section 12. Three synthetic situations, each with a regression slope that looks like an effect.

**A. Coaching.** Students who coach more hours score more. In the data, `score ~ hours` gives a slope of 4.5 marks per hour, but `score ~ hours + ability` gives 2.0. The true effect (by construction) is 2.0.

**B. A random assignment.** The same study, but now a coin decides how many hours each student coaches (assignment is independent of ability). `score ~ hours` gives 1.9, and `score ~ hours + ability` gives 2.0.

**C. Two random walks.** Two completely unrelated random walks (cumulative sums of random steps), 100 points each, are regressed on each other. In 200 repeated trials the slope's p-value was below 0.05 in **151** of them.

Write your answer in `answer.md`:

1. In A, why did the first slope overstate the effect, and what is the name of `ability`? Give the bias formula in words.
2. In B, why did omitting `ability` **not** matter?
3. In C, a valid test of "no relationship" should reject about 10 times out of 200. Which assumption failed and what does it show about p-values?
4. When can adding a control variable make an estimate **worse**? Name two kinds of variable.

## After you answer

Compare with the model answer and tick the checklist for the points you made.
