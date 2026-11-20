## Hint 1

Which question comes first: "who is it?" or "what do they want?" If you check the role first, how many separate branches do you need? What should happen when the role is none of the three?

## Hint 2

Write a rule only when something is **allowed**. Then ask: what does the function return when no rule fires? That answer is the deny-by-default. For a customer, which two facts must be true to cancel (ownership and status)? What if `order` is `None`?

## Hint 3

```text
if user is None: return False
if role == admin:    return action in {read, cancel, refund, list_all}
if role == support:  read / list_all -> True; refund -> order given and amount <= limit; else False
if role == customer: need order; read -> owns; cancel -> owns and pending; else False
return False                      # unknown role, last line
```
