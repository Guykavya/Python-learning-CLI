## Hint 1

You need a vertex that Dijkstra settles **early**, through a cheap direct edge, while a route that first goes somewhere more expensive and then takes a negative edge is cheaper in the end. With vertices 0, 1, 2: which vertex should be the "cheap but wrong" one, and where does the negative edge go?

## Hint 2

Try `0 -> 1` cheap, `0 -> 2` more expensive, and `2 -> 1` negative enough to beat the direct edge. Run the given code to check. For question 3, add the same number to all three weights of your example and compare the two routes from 0 to 1 again: one has 1 edge, the other 2.
