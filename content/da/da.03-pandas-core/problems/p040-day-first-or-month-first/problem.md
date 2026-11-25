# Day first or month first?

Chapter sections 13.1 and 13.2. A file from a shop has an `order_date` column with values such as `03/04/2024`,
`13/02/2024` and `07/08/2024`. Nobody wrote down the format. A colleague says: "Just call `pd.to_datetime` and be done."

```python
import pandas as pd

pd.to_datetime(pd.Series(["01/02/2024", "13/02/2024"]))     # ValueError in pandas 3
pd.to_datetime(pd.Series(["03/04/2024"]), format="%d/%m/%Y")  # 3 April
pd.to_datetime(pd.Series(["03/04/2024"]), format="%m/%d/%Y")  # 4 March
```

Explain in `answer.md`, in about 150 to 250 words:

1. Why is `03/04/2024` **dangerous**? What does pandas do when a column mixes day-first and month-first rows?
2. How can you **decide** which order a file uses? Name at least two clues in the data and one outside it.
3. After you choose, how do you make the choice visible and check it?

## Example

A start: "`03/04/2024` is 3 April in Delhi and 4 March in New York. Both readings are valid dates, so the text alone
cannot tell them apart..."
