## Approach

The model answer is in `answer.md`. Use the complaint's *symptom* to find the principle:

| Symptom you notice | Principle |
|---|---|
| many unrelated reasons to open the same file | S |
| adding a feature means editing old, tested code | O |
| a subclass breaks code written for its parent | L |
| classes must stub methods they do not need | I |
| cannot replace or fake a collaborator in a test | D |

Snippet 4 shows both I (the interface is too fat) and L (the stub raises, so substitution fails).
Notice that the fixes are small: a dict, a parameter, a split. SOLID is a set of reasons for
small changes, not a reason for big frameworks (see p017).

## Check your answer

- Did you name two principles for snippet 4?
- Is every fix concrete (a dict, a parameter, a split), not just "use a pattern"?
- For 3, did you avoid "just override `set_height` too"? That keeps the same broken contract.
- Did you separate the *symptom* (cannot test) from the *principle* (D)?

## Another way

Python offers light tools for each principle: functions and registries for O, duck typing and
`typing.Protocol` for I and L, plain parameters for D, and modules and small classes for S.
