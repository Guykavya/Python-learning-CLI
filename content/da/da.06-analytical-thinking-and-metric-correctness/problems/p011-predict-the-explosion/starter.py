def rows_after_join(a, b, key):
    """Predict len(a.merge(b, on=key)) (inner join) WITHOUT merging. `key` is a column name or a list of names."""
    raise NotImplementedError("count the rows of each key value on both sides, multiply, add up")
