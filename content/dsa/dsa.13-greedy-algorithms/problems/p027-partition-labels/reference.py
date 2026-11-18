def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}      # the last index wins
    sizes = []
    start = 0
    end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:                               # no letter in the piece appears later
            sizes.append(i - start + 1)
            start = i + 1
    return sizes
