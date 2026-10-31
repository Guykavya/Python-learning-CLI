## Hint 1

Start with the simplest question: after `double_u(5)`, what type does the checker believe the result has? Is it still an `int`? Compare with `double_a(5)`.

## Hint 2

A constraint list is a closed set: the argument is matched to **one entry** and `A` becomes exactly that entry. A bound is an upper limit: `B` becomes the real type of the argument as long as it fits under the limit. What does each give for a subclass like `MyInt`?

## Hint 3

For question 3, think about *how many times* the checker reads the body. With constraints it can read the function once with `A = int` and once with `A = str`. With a bound or a union it reads it once, with a type that might be `int` or `str` independently for each `x`.

For question 4, think of one example for each: "any Sized thing", "str or bytes but never mixed", "int or str in, always str out".
