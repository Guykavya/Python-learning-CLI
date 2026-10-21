## Hint 1

You do not know in advance how many guesses there are. Which loop runs "until something happens"?
Where in the loop should you read the next guess?

## Hint 2

Use `while True:` and read one guess at the start of each pass. Check "out of range" **first**, and skip the
rest of the pass with `continue` before the counter goes up. Leave the loop with `break` after printing `correct`.

## Hint 3

```
secret = read number
count = 0
repeat forever:
    g = read number
    if g < 1 or g > 100: print "out of range", go to next pass
    count += 1
    if g < secret: print "higher"
    elif g > secret: print "lower"
    else: print "correct in", count, "guesses" and stop the loop
```
