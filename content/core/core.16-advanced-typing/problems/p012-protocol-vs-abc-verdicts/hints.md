## Hint 1

For each call, ask what the parameter type is: `Closeable` (a Protocol) or `Shape` (an ABC). For a Protocol, compare the **shape**: does the argument's class have a method `close` with a compatible signature (same parameters, `-> None`)? For an ABC, ask only: does the class inherit from it?

## Hint 2

`Socket.close` needs one extra argument (`force`). Can a `Closeable` user call `c.close()` with no argument? `Circle` has the right method `area`, but `Shape` is an ABC: inheritance is the only way in. `open(...)` returns a file object that has `close()` with no extra arguments.

## Hint 3

For `H`, `I`, `K`: what is the rule for creating an instance of an abstract class? A Protocol method whose body is only `...` is treated as *abstract* when a class inherits from the protocol explicitly. And a protocol class itself: can it be instantiated?
