# Population stability index

Chapter section 14.7. In production the world changes. The **population stability index** compares the distribution of a feature (or of the model's scores) now with its distribution in training: bin the training values into deciles, then sum `(share_now - share_then) * ln(share_now / share_then)` over the bins. A common reading: below 0.1 stable, 0.1 to 0.25 a moderate shift, above 0.25 a major shift (a convention, not a law).

The chapter compared the training distribution of `monthly_charge` with three simulated production months:

```text
same distribution         PSI =   0.002
15% price rise            PSI =   0.191
paise instead of rupees   PSI =   8.283
```

Your model runs every night. This week the monitoring shows: feature `monthly_charge` **PSI 0.05**, feature `support_calls` **PSI 0.15**, and the model's **output score PSI 0.4**.

Write your answer in `answer.md`:

1. What does each of the three values mean, and what would you do for each (no action, investigate, act)?
2. Why is a large PSI on the **score** more urgent than a moderate PSI on one input?
3. Name two causes of a high PSI that are **not** a change in the customers (think of the "paise" row).
4. Why is PSI alone not enough to decide to retrain? What else would you look at?

## After you answer

Compare with the model answer and tick the checklist for the points you made.
