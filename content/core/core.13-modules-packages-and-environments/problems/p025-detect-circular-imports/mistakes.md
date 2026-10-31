- Using only "visited / not visited". Then a diamond (two roads to `base`) looks like a cycle. You need
  to know whether the module is still in progress.
- Returning the whole path as the cycle. The modules before the repeated one lead to the loop but are
  not in it. Cut the path at `path.index(dep)`.
- Starting the search only from the first module. Separate parts of the graph are never checked.
- Using `graph[dep]` for modules that only appear in lists: `KeyError`. Use `graph.get(dep, [])`.
- Appending a module when you **start** it instead of when it is done. Then a module comes before its
  imports.
- Sorting the lists in place (`graph[m].sort()`), which changes the caller's data.
