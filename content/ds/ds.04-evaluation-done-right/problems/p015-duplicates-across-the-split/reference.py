def cross_split_duplicates(train, test, cols):
    seen = set(map(tuple, train[list(cols)].itertuples(index=False, name=None)))
    hits = [label for label, row in zip(test.index, test[list(cols)].itertuples(index=False, name=None)) if row in seen]
    return len(hits), sorted(hits)
