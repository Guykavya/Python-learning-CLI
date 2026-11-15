def largest_rectangle(heights):
    best = 0
    for h in heights:
        best = max(best, h)      # TODO: this only looks at rectangles of width 1
    return best
