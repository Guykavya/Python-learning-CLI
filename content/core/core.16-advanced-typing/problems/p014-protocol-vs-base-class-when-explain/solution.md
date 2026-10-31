See the model answer shown when you check. The ideas that must appear:

1. Nominal = must inherit (base class, ABC); structural = has the right members (Protocol, duck typing the checker understands).
2. Part 1: Protocol, because users and third-party classes cannot or will not inherit from your class. Part 2: ABC, because you own the classes, they share code, and `@abstractmethod` fails at creation.
3. Protocol for Part 2: no inherited shared code, a missing method is found late. ABC for Part 1: everybody must inherit from (or be registered with) your class, third-party code needs wrappers.
4. `@runtime_checkable` gives `isinstance` but only checks that the names exist, not signatures or types.
