# A median for an ordinal scale

Chapter section 6.4. Survey answers such as *strongly disagree ... strongly agree* are **ordinal**: they have an order but no distances, so the **mean of the ranks is suspect** (is the gap between "disagree" and "neutral" the same as between "agree" and "strongly agree"?). The **median** needs only the order.

Write `ordinal_median(responses, order)`. `order` lists the labels from lowest to highest; `responses` is a list of labels.

- Odd count: return the middle label.
- Even count: take the two middle labels. If they are the **same**, return it. If they differ, return a tuple `(lower_label, upper_label)`: there is no honest label halfway.
- A label not in `order`: `ValueError` whose message contains the bad label.
- No responses: `ValueError`.

## Example

```python
order = ["disagree", "neutral", "agree"]
ordinal_median(["agree", "disagree", "neutral"], order)        # 'neutral'
ordinal_median(["agree", "agree", "neutral", "disagree"], order)   # ('neutral', 'agree')
ordinal_median(["agree", "agree", "neutral", "neutral"], order)    # ('neutral', 'agree')
ordinal_median(["agree", "agree", "agree", "neutral"], order)      # 'agree'
```
