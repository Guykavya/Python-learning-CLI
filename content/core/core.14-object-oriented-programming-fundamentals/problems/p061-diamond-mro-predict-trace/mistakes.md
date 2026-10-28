- Depth-first order `Bottom, LogMixin, Left, Base, Right`. C3 puts `Base` after **all** classes
  that inherit from it.
- Thinking `LogMixin` stops the `__init__` chain or the `hello` chain. It has no `__init__`, so the
  search just continues; its `hello` calls `super()`, which goes on to `Left`.
- Printing `Base init` twice. Cooperative `super()` visits each class once.
- Writing `['Left', 'Base']` for `Left.hello(b)`. `super()` uses the MRO of `b`, where `Right`
  follows `Left`.
- Writing `['Left', 'Right', 'Base']` for `Left().hello()`. A plain `Left` object has no `Right` in
  its MRO.
- Writing `Left init start` first for `Other()`. `Other(Right, Left)` lists `Right` first.
- Thinking `Mixed(Bottom, Other)` works because both are fine on their own. They disagree about the
  order of `Left` and `Right`, so C3 fails.
