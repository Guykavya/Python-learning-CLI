- Depth-first, left-to-right with duplicates removed (keep first): gives `D, B, A, C` for the
  diamond. That was Python 2's classic rule, and it lets `A` override `C`.
- Depth-first keeping the **last** duplicate: gets the diamond right, but cannot detect inconsistent
  hierarchies and is wrong on some larger ones.
- Forgetting the list of bases `[B1, ..., Bn]` as the last list in the merge. Then the order of the
  bases is not respected.
- Taking the first good head and then continuing the scan in the **same** round. After each choice,
  start again from the first list.
- Removing the chosen head only from the list it came from. It must go from every list it heads.
- Modifying the lists in `bases_map` (with `del` or `pop`) instead of copies. The second call then
  gives a different answer.
- Leaving out `object` at the end, or adding it twice.
