## Model answer

1. **A** The omitted variable `ability` is a **confounder**: able students both coach more and score higher, so the `hours` coefficient absorbs part of the effect of ability. The bias equals the effect of the omitted variable times the slope of the omitted variable on the included one: `5 * cov(hours, ability) / var(hours)`. Adding the confounder moves the slope from 4.5 to the true 2.0. More data would not remove this bias.
2. **B** Because the hours were assigned by a coin, they are unrelated to ability. A confounder must be related to both the treatment and the outcome; here the first link is cut by randomisation, so omitting `ability` only adds noise (a wider interval) and not bias. The two slopes (1.9 and 2.0) agree within noise.
3. **C** The **independence of errors** assumption fails: random walks drift, so neighbouring errors are strongly related. The regression's standard errors are too small, p-values are meaningless, and 151 of 200 "significant" results show that a "significant" p-value only means something if the model's assumptions hold. Correlation can appear from nothing.
4. Adding a control can hurt when it is a **mediator** (caused by the treatment and on the path to the outcome: controlling removes part of the effect you want) or a **collider** (caused by both the treatment and the outcome: controlling for it creates a false association). Which variables are good controls is a question about the causal story, which statistics alone cannot answer.

**Checklist: your answer should mention**
- [ ] `ability` is a confounder related to both hours and score
- [ ] the bias formula: the omitted variable's effect times its slope on the included variable
- [ ] more data does not fix omitted-variable bias
- [ ] randomisation breaks the link between treatment and confounders, so omitting ability only costs precision
- [ ] random walks violate independence of errors, so p-values are invalid
- [ ] a mediator and a collider as bad controls
- [ ] the wording "associated with" unless the design supports "causes"
