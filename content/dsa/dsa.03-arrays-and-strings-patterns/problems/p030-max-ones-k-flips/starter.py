n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]
# TODO: a window may hold at most k zeros; grow it with r, shrink it with l while it holds too many
print(a.count(1))
