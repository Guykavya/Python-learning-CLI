## Hint 1

For each line, write down the type of the value that is passed or assigned, and the type that is expected. A literal written in the call, like `"r"`, has the type `Literal["r"]`. Is that one of the allowed values?

## Hint 2

Lines `A`, `D` and `I` all involve a variable. What type does the checker give to `m = "w"` (an ordinary assignment, no hint)? To the parameter `s: str`? And how is `n: Final = "w"` different from `m = "w"`?

## Hint 3

`H` and `I` are a pair: `Literal["a"]` into `str`, and `str` into `Literal["a"]`. One direction narrows the type (the checker would have to guess which string), the other widens it. Which is safe?
