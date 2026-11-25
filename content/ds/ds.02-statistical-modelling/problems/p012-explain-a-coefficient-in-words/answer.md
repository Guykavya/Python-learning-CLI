## Model answer

1. **level-level, 4.7**: holding the other variables fixed, one extra hour of study per week is associated with **4.7 more marks**.
2. **log-level, 0.025**: holding the others fixed, one more year of experience is associated with about **2.5% higher wage** (the shortcut `100 * b`). Exactly, `100 * (exp(0.025) - 1) = 100 * 0.0253 = 2.5%`. The shortcut is close because b is small.
3. **log-log, 0.80**: this is an **elasticity**: a 1% larger floor area is associated with about **0.8% more sales**, holding the others fixed.
4. **dummy, 0.18**: people with a degree earn, holding the others fixed, about **19.7% more** than the baseline group (school): `100 * (exp(0.18) - 1) = 19.7`, not 18. The gap between 18 and 19.7 shows that the shortcut `100 * b` gets worse as `b` grows, because the model is linear in the logarithm, so changes are multiplicative.

**Checklist: your answer should mention**
- [ ] "holding the other variables fixed" in the sentences
- [ ] "associated with", not "causes"
- [ ] case 1 stated in marks per hour (level-level)
- [ ] case 2 as percent per year, with the exact value 2.5%
- [ ] case 3 as an elasticity: 1% in area goes with 0.8% in sales
- [ ] case 4 compared with the baseline (school) and the exact 19.7%
- [ ] the exact percent is `100 * (exp(b) - 1)` and the shortcut `100 * b` drifts for big b
