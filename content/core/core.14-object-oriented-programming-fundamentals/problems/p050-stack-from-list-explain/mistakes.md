- "It works, so it is fine." It works for the three methods Ravi calls. The problem is all the other
  list methods and operations anyone else can call.
- Listing only `insert`. `sort`, item assignment, `pop(0)`, `del`, `remove`, `reverse`, `clear`,
  slicing and `+` all break or bypass the rule.
- Overriding every bad method to raise an error. That is a long, fragile blacklist (new list
  methods would leak again), and `isinstance(s, list)` is still a lie.
- Storing the list in a public `self.items`. Callers then use `s.items.insert(0, x)` and the leak is
  back. Use `self._items` and methods.
- Saying "never inherit". Inheritance is right when the subclass really is a parent and keeps all its
  promises, for example in exception hierarchies.
