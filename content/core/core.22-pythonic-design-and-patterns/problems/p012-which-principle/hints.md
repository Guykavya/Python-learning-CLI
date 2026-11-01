## Hint 1

Turn each complaint into a question. "We edit it for three reasons" -> how many reasons to
change? "I edit it to add a new kind" -> must I edit, or could I only add? "It gives a
surprising result with a subclass" -> can the child stand in for the parent? "It must
implement things it cannot do" -> is the interface too big? "I cannot test it" -> who creates
the collaborator?

## Hint 2

```
1 several reasons to change  -> S
2 edit to add a new kind     -> O
3 child surprises caller     -> L
4 forced to stub + crashes   -> I and L   (the double one)
5 builds MySQL inside        -> D
6 builds the SMS client      -> D
```
For each, write: principle, one-sentence reason, smallest fix (a line of code is best).
