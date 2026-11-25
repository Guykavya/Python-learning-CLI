# Which gradient is wrong?

Chapter section 7.3. Three functions of `w = [w1, w2]` and a hand-derived gradient for each:

| | function | claimed gradient |
|---|---|---|
| A | `(2 w1 - w2)^2` | `[4 (2 w1 - w2), -2 (2 w1 - w2)]` |
| B | `exp(w1^2) + w2` | `[exp(w1^2), 1]` |
| C | `sin(w1 w2)` | `[w2 cos(w1 w2), w1 cos(w1 w2)]` |

In `answer.md` (about 150 to 250 words):

1. say which gradient is wrong and **which term is missing**, and name the rule that was forgotten;
2. explain how a **gradient check** at the point `w = [1, 0.5]` reveals the mistake: what it computes and what size of relative error you expect for a correct and for a wrong gradient;
3. say what you would change.

## Example

A start: "A numerical gradient does not use any formula, so if the formula is wrong, the two disagree..."
