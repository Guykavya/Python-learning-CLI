- `groups.get(letter, []).append(word)`. `get` returns a new list but does not store it, so the
  word is lost.
- Using `word[0]` without `.lower()`, giving separate `A` and `a` groups.
- Lowercasing the words themselves. Only the key is lowercased.
