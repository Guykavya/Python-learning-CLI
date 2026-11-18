def assign_cookies(greed, sizes):
    greed = sorted(greed)
    sizes = sorted(sizes)
    child = 0
    for cookie in sizes:
        if child < len(greed) and cookie >= greed[child]:
            child += 1                  # this child is happy; move to the next one
    return child
