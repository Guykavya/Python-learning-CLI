def relationship(left, right, left_key, right_key):
    left_unique = bool(left[left_key].is_unique)
    right_unique = bool(right[right_key].is_unique)
    kind = {(True, True): "1:1", (True, False): "1:m", (False, True): "m:1", (False, False): "m:m"}[(left_unique, right_unique)]
    left_orphans = int((~left[left_key].isin(right[right_key])).sum())
    right_orphans = int((~right[right_key].isin(left[left_key])).sum())
    return {"relationship": kind, "left_orphans": left_orphans, "right_orphans": right_orphans}
