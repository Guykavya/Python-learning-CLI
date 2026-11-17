# Explain: why is DSU nearly `O(1)`?

Chapter section 9 says that with **union by size** and **path compression**, any sequence of `m` Union-Find operations on `n` elements costs `O(m α(n))`, "practically `O(1)` per operation". This problem asks you to explain where that comes from, at least the parts you can prove with simple counting.

Write a short explanation (12 to 18 sentences) in `answer.md` that answers:

1. **No tricks.** With `parent[find(x)] = find(y)` and a plain `find`, the chapter builds a chain by `union(i, i + 1)` for `i = 0 .. n-2`. How deep is element 0 at the end? What do `n` calls of `find(0)` cost?
2. **Union by size: the doubling argument.** When does an element become one level deeper? Show that each time this happens, the size of the element's group **at least doubles**. Why does that make every depth at most `log2(n)`, and every `find` `O(log n)`?
3. **A worked example.** With union by size only (no compression), which sequence of unions on 8 elements builds a tree of height 3? Why can no sequence on 8 elements build height 4?
4. **Path compression.** What does `find` do to the path it walks? Why does one slow `find` make the next `find`s on the same elements fast?
5. **Amortised.** "Nearly `O(1)` per operation" is an **amortised** statement. What does that mean? Can a single `find` still take more than one step?
6. **The α.** The chapter says `α(n) ≤ 4` for any `n` you will ever store. In one or two sentences, what kind of function is α, and why can you treat it as a constant? (You do not need to define the Ackermann function.)
7. **The price.** Union-Find can merge groups but not split them, and cannot list the members of a group quickly. Why are these the limits of the "trees pointing up" design? When would you use BFS instead (chapter section 9, "Union-Find or BFS?")?

Then compare with the model answer and rate yourself.
