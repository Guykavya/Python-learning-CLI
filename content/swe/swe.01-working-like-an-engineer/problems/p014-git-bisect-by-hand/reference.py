def first_bad(commits, is_bad):
    lo = 0                     # known good
    hi = len(commits) - 1      # known bad
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if is_bad(commits[mid]):
            hi = mid
        else:
            lo = mid
    return commits[hi]
