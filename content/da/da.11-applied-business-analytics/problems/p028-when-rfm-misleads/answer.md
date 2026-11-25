## Model answer

**Gift shop (seasonal).** After December, recency is large for almost everybody because they bought in the pre-Christmas weeks and nothing since: the "At risk" and "Hibernating" segments would hold nearly all customers, and a win-back campaign in February
would target people who behave exactly as they do every year. Instead, compute recency against the **same season** a year earlier, or score customers on their behaviour in last year's peak (did they buy last December? this December?), and judge a customer
by the **seasonal** rhythm, not by days since last order.

**Streaming subscription.** Every active customer pays every month, so **frequency and recency carry no information** (everyone scores the same), and money is the same price for everybody. RFM cannot tell a customer about to cancel from a happy one.
Use **tenure**, usage (hours watched, logins), payment problems and plan type, and a **churn model** or a survival analysis for the risk of cancelling.

**B2B supplier with one huge order.** The 4 million order makes that customer "Champion on M" and pushes everybody else down by one quantile if scores are rank-based, and with scores based on raw values the others all look the same.
Treat the outlier on its own (an account manager, not a segment), **cap or log** the monetary value, and score the remaining customers by quantiles. Check with the future spend of each segment that the scores still predict.

**Checklist: your answer should mention**
- [ ] seasonality: recency is large for everyone after the peak; compare with the same season last year
- [ ] subscription: frequency and recency are constant, so RFM tells nothing; use tenure, usage, cancellation risk
- [ ] an outlier distorts the monetary quantiles; treat it separately or cap/log the values
- [ ] test any segmentation on future behaviour
