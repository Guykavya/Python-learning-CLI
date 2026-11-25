## Hint 1

Start from the timeline: when is `retention_offer_sent` written, and when do we have to predict?

## Hint 2

In the future data the column is 0 for everybody. AUC only cares about order: what does a constant column do to an order? And what does a model that learned 'no offer = safe' predict for everybody?
