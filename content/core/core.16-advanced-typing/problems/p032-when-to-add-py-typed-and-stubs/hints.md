## Hint 1

Think of what the type checker needs to find for an installed package: where does it look, and how does it know the author *wants* the hints to be used? What does a separate stub package do for a library you cannot change?

## Hint 2

Karan has three roads: borrow someone's types, write his own, or switch checking off for that import. What type does the module get in the third case, and what does `Any` do to code that touches it (you saw this in the Any versus object problems)?

## Hint 3

For Isha, think "small steps with a safety net": which flags can be turned on for part of the code only? Which functions matter most to type first? What stops the typed part from getting worse later?
