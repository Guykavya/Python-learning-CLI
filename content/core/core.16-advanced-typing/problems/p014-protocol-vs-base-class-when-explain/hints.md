## Hint 1

Define the two words with one small example each. "Is a `Dog` an `Animal`?" can be answered by looking at *what the class declares*, or at *what the class can do*. Which of these is which?

## Hint 2

Part 1: who controls the classes that must fit? Can they be made to inherit from your class? Part 2: who controls the classes, and is there shared code? When should a missing method be reported: while checking the code, or already when `Backend()` is called?

## Hint 3

For question 4, split it: (a) what does a type checker need `isinstance` for? (b) what does `@runtime_checkable` allow at runtime? (c) what is the limit (hint: look at what `hasattr` can and cannot tell you).
