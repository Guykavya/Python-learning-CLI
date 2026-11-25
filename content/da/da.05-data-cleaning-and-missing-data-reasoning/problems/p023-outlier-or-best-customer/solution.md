## Approach

The model answer in `answer.md` treats each suspect as a different kind of case from chapter 6.1: **real but extreme**
(keep, flag, report the effect), **impossible** (set to missing, flag, check the source) and a **machine fault that
looks plausible value by value** (a stuck run). Rate your answer against the checklist at the end of `answer.md`.

## Complexity

Nothing to compute. The cost of a wrong decision is a wrong mean (one order of 9,00,000 can double a small mean) or a
lost customer.

## Another way

Answer with a table: suspect | kind | action | what I check | what I report. Writing the four columns forces you to
make the four decisions. Then add the sentence about never deleting silently.
