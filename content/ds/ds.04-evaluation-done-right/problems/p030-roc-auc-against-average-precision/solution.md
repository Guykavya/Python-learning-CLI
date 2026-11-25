## Walk-through

Four positives (ranks 1, 3, 4, 7), six negatives. Negatives below each positive: rank 1: 6; rank 3: 5; rank 4: 5; rank 7: 3. Pairs = 19 of 4 * 6 = 24. AUC = 0.792.

Precision at the hits: 1/1 = 1.0, 2/3 = 0.667, 3/4 = 0.75, 4/7 = 0.571. AP = (1 + 0.6667 + 0.75 + 0.5714) / 4 = 0.747.

## Moving a positive to the bottom

AUC loses 3 pairs (19 -> 16 of 24: 0.667). AP replaces 4/7 by 4/10 (0.571 -> 0.4): AP changes from 0.747 to 0.704. Here AUC moves more; AP moves most when the **top** of the list changes (swap the first two rows and AP drops much more than AUC).
