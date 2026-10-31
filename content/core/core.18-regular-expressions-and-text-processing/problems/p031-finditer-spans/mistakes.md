- Using `re.findall` and then `text.find(word)` to get positions: `find` always returns the
  **first** occurrence, so repeated words all get the same position.
- Writing `(m.start(), m.end() - 1)`. Python ends are exclusive; `m.end()` is already right for slicing.
- Filtering out empty matches with `if m.group():`. The task says zero-width matches count.
- Expecting overlapping matches (`(1, 3)` in `"aaaa"`). The search always continues at the end of
  the previous match. Overlaps need a lookahead like `(?=(aa))`.
- Calling `re.search` in a loop with a hand-moved start index and forgetting to step forward after
  an empty match, which loops forever. `finditer` handles that for you.
