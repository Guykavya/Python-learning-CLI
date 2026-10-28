**1. Nominal vs structural.** In *nominal* typing a class is a `Shape` only if it says so, by
inheriting from `Shape`. In *structural* typing a class counts if it has the right members and
signatures, no matter what it inherits from. A normal base class or `ABC` is nominal. A
`Protocol` is structural: it is duck typing, made checkable.

**2. The choice.** **Part 1 is a Protocol**: `class Exporter(Protocol): def export(self, rows) -> str`.
The third-party CSV exporter cannot be changed to inherit from my class, and other teams do not
even import my package, yet any object with a matching `export` works and the checker can
verify it. **Part 2 is an ABC** (or a normal base class): the three backends are mine, they
share real code (`save`), and `@abstractmethod` on `_write` makes Python refuse to create a
backend that did not implement it. That is the "fail at creation" requirement.

**3. What is lost.** With a Protocol for Part 2 there is no shared implementation to inherit
(a protocol can hold default methods, but only if classes inherit from it explicitly), and a
backend that forgets `_write` is only discovered by the type checker, or when the method is first
called, not when the object is created. With an ABC for Part 1 every user class, including the
third-party one, must inherit from my ABC (or be registered), which couples them to my package
and often means writing wrapper classes.

**4. About `isinstance`.** The friend is only half right. The type checker verifies protocols
without `isinstance`, but at runtime (say when loading user plugins) a Protocol is nothing
without help. `@runtime_checkable` makes `isinstance(x, Exporter)` work, but it only checks that
the *names exist*: not the argument types, not the return type, not the type of an attribute.
`isinstance` is therefore a shallow check; use it as a guard, and let the type checker do the
real verification. (Also, `issubclass` does not work with protocols that have data members.)
