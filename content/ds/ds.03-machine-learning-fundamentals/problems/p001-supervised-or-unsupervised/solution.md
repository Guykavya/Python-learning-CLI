## Walk-through

1. "predict" matches the first rule: `supervised`.
2. No word of the first rule; "group" matches the second: `unsupervised`.
3. "classify": `supervised`.
4. "unusual" is not "anomal", and none of the other words appears: `unclear`.
5. "forecast": `supervised`.
6. First rule: none. Second rule: "cluster" (in "clusters"): `unsupervised`.
7. "predict" matches first: `supervised`.
8. First rule: none. Second rule: "anomal" (in "anomalies"): `unsupervised`.

## The two wrong ones

- Line 4 (`unclear`): finding unusual transactions is **anomaly detection**, normally unsupervised (no one labelled the unusual ones). The rule missed it because it looks for a word, not for the idea.
- Line 7 (`supervised`): clustering patients is **unsupervised**. The word "predict" appears in the sentence, and the first rule wins. (If patients had known outcomes, "predict who is at risk" would be supervised; the sentence mixes both ideas.)

## Another way

Ask one question: *does every training row carry the answer I want to predict?* If yes, supervised.
