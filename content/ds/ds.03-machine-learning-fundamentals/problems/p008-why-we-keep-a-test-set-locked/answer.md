## Model answer

1. The test set was used to **choose** among 30 models, so it became a validation set. The score of the winner is partly skill and partly luck on those particular rows. Picking the best of many noisy scores keeps the luckiest, so the reported number is biased upwards. It no longer estimates performance on new data.
2. Expect the best of 30 to be **above 90%**, perhaps 94-95%. Each model has noise of about 3 percentage points on 100 rows (`sqrt(0.9 * 0.1 / 100) = 0.03`); the maximum of 30 such scores is typically about two standard deviations above the true value, even though no model is better than 90%.
3. Split the data into three parts: training (fit), validation (compare models and tune, or use cross-validation on the training data), and a **test set that is opened once**, for the single chosen model. Report that one number, with its uncertainty. If a second look is needed, collect new data.

**Checklist: your answer should mention**
- [ ] the test set was used for selection, so it is no longer independent
- [ ] "best of many" is biased upwards (winner's curse)
- [ ] the best of 30 equally good models scores above the true value
- [ ] use a validation set (or cross-validation) for choosing
- [ ] open the test set once, at the end, for one model
