h = int(input())
u = int(input())
d = int(input())

if u >= h:
    # It climbs out on the very first day; the night never comes.
    print(1)
elif u <= d:
    # It never gains height overall, and one climb is not enough.
    print("never")
else:
    gain = u - d          # net progress per full day and night
    need = h - u          # morning height needed so that one more climb is enough
    full_days = (need + gain - 1) // gain    # ceiling of need / gain, with integers only
    print(full_days + 1)
