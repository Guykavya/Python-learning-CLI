## Approach

The model answer in `answer.md` goes question by question. The core idea of the chapter is that the **cause** of the
missingness decides the damage: nothing (no bias), a visible column (bias that visible columns can undo), or the hidden
value (bias that the data cannot undo). Rate your answer against the checklist at the end of `answer.md`.

## Complexity

Nothing to compute. In the chapter's simulation, 23 percent of 6,000 incomes were hidden each way, and the observed mean
moved from 34,341 (truth) to 34,356 (MCAR), 36,271 (MAR) and 30,070 (MNAR): the same amount missing, three different
answers.

## Another way

Explain it with a picture: three scatter plots of income against education. MCAR hides random points; MAR hides the
points on the left (low education); MNAR hides the points at the top (high income). Then say what the average of the
visible points does in each plot.
