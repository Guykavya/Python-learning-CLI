# Explain leakage to a colleague

The module's first outcome: *explain data leakage.* Use the churn story of chapter section 1. A model scored ROC-AUC 0.968 in cross-validation with the column `retention_offer_sent`, and 0.759 without it. In this company the retention offer is sent **when a customer calls to cancel**. Trained with the column and tested on future customers (for whom no offer has been sent yet), the model gave:

```text
honest model on the future: AUC 0.770 | mean predicted probability 0.240 (true churn rate 0.235) | recall at 0.5: 0.223
leaky  model on the future: AUC 0.778 | mean predicted probability 0.024 (true churn rate 0.235) | recall at 0.5: 0.000
```

Write a short explanation (about 150-250 words) in `answer.md` for a colleague who built the model. Cover:

1. what **data leakage** is, in one or two sentences;
2. why the cross-validated score of 0.968 **lied**, using the story of the offer column;
3. what the two lines above show (both the AUC and the probabilities);
4. the **golden rule** and the question to ask of every column;
5. one other family of leakage they should check for next.

## After you answer

Compare with the model answer and tick the checklist for the points you made.
