## Approach

Contrast the two objects by what they hold. A list holds results; a generator holds a recipe and a
bookmark. Every difference follows from that: memory, one-time use, no `len`, no indexing, and the
ability to stop early.

## Model answer

See `answer.md`.

## Complexity

List: O(n) memory, built at once. Generator: O(1) memory, each item computed when asked.

## Another way

A list is a printed book: heavy, but you can open any page any time. A generator is a person reading
the book aloud to you: costs nothing to carry, but you hear each page once, in order, and you
cannot ask for page 10 directly.
