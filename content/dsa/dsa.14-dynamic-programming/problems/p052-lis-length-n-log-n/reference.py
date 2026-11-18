from bisect import bisect_left


def lis_len(nums):
    tails = []                           # tails[k]: smallest end of an increasing run of length k+1
    for x in nums:
        k = bisect_left(tails, x)        # first tails[k] >= x
        if k == len(tails):
            tails.append(x)              # x extends the longest one
        else:
            tails[k] = x                 # a length-(k+1) subsequence can now end lower
    return len(tails)
