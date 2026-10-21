## Hint 1

One method does the replacing. Which method tells you how many times something occurs?

## Hint 2

`replace` replaces every occurrence and `count` counts non-overlapping occurrences, scanning left to right in the same way. So the count of the old word is the number of replacements.

## Hint 3

```
sentence = input()
old = input()
new = input()
print(sentence.replace(old, new))
print("Replacements:", sentence.count(old))
```
