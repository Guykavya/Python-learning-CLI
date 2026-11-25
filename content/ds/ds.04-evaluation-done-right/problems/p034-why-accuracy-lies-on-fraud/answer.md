## Model answer

1. "Never fraud" is correct on every legitimate transaction: 998 of 1,000 = **99.8%** accuracy, while catching **zero** fraud. Accuracy is dominated by the majority class.
2. Report numbers about the rare class:
   - **Recall** (sensitivity): of all frauds, the share caught.
   - **Precision**: of the transactions flagged, the share that really are fraud (how many alarms are wasted).
   - **Average precision / the precision-recall curve**: ranking quality focused on the positives, better than ROC-AUC when positives are rare.
   - The **confusion matrix** in counts, and the **cost** of errors (a missed fraud vs a wasted review).
3. With a capacity of 500 reviews a day, report **precision at k = 500** (how many of the reviewed transactions are fraud) and **recall at k = 500** (what share of the day's frauds is reviewed). The threshold is then simply "the top 500 scores".

**Checklist: your answer should mention**
- [ ] never flagging gives 99.8% accuracy and catches no fraud
- [ ] recall: share of frauds caught
- [ ] precision: share of alarms that are real
- [ ] precision-recall curve or average precision for rare events
- [ ] precision and recall at k for a fixed review capacity
