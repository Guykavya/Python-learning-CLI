# Top scorer with max and a key

`scores` is a dict from player name to score. Write `top_scorer(scores)` that returns the name of
the player with the **highest** score. If several players share it, return the one that comes
**first alphabetically**. For an empty dict return `None`.

Use `max` or `min` with a `key=lambda ...`; no explicit loop needed.

**Examples**

```python
top_scorer({"Ravi": 40, "Asha": 55, "Meena": 50})   # 'Asha'
top_scorer({"zoya": 60, "kiran": 60, "anu": 10})    # 'kiran'
top_scorer({})                                      # None
```
