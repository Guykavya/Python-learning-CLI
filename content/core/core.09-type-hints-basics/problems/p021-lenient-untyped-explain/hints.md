## Hint 1

Which of the three functions has no hints at all? What does mypy assume about a call to such a function, and does it look inside its body?

## Hint 2

`average([])` passes a perfectly good `list[float]`. What does the crash come from: the type of the argument, or its value (its length)? Which chapter taught you tests and error handling?

## Hint 3

Think of the two escape hatches you have seen: a type that means "anything" and a comment at the end of a line. What do you lose when you use them?
