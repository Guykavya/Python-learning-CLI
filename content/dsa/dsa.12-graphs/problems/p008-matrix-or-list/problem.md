# Explain: matrix or list?

Chapter section 2 shows three ways to store a graph: an edge list, an adjacency list and an adjacency matrix. Choosing well is often the difference between a program that runs and one that does not fit in memory.

Write a short explanation (8 to 14 sentences, numbers welcome) in `answer.md` that answers:

1. A road map has `V = 100,000` towns and `E = 300,000` roads (undirected). Estimate the number of stored entries for an adjacency list and for an adjacency matrix. Which one can you even build?
2. A social group has `V = 2,000` people and almost everyone knows almost everyone: about `E = 1,900,000` friendships. Is the matrix still a bad idea? Compare the two sizes again.
3. Give the cost of these three operations for each of the two structures: "is `u-v` an edge?", "list the neighbours of `u`", "visit every edge once" (the last one is what BFS and DFS do).
4. Define **sparse** and **dense** in terms of `E` and `V`. Which kind is a grid of `R x C` cells, and why?
5. You run BFS on an adjacency matrix with `V = 20,000` vertices and only `E = 40,000` edges. Why is it slow, although the graph is small? Write the cost.
6. Name a structure that gives `O(1)` (average) edge tests **and** `O(degree)` neighbour lists with `O(V + E)` memory.

Then compare with the model answer and rate yourself.
