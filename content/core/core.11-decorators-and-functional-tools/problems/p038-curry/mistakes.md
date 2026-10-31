- Keeping one shared list and doing `saved.extend(args)`. After `base(3)(4)`, `base` remembers
  3 and 4 as well, and `base(5)` calls `func` too early with the wrong numbers.
- Same bug with keywords: `saved_kwargs.update(kwargs)` changes the dict that other branches share.
- Counting every parameter with `len(signature.parameters)`. Parameters with defaults are then
  treated as required, and `greet("Hi")("Ann")` waits for a third argument.
- Using `==` instead of `>=`. If someone passes more arguments than required (for example a
  value for a parameter with a default), the function never gets called.
- Calling `func` inside `curry` to "test" it.
- Forgetting `wraps` on the inner curried functions: only the first one keeps the name.
