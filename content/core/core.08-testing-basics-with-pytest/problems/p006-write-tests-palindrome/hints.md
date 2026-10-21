## Hint 1

List the kinds of input: a plain palindrome, a plain non-palindrome, mixed case, text with spaces, the empty string, one letter. Which of these would a lazy implementation get wrong?

## Hint 2

A function that only compares the first and last letters says `"abca"` is a palindrome. Which input would catch it?

## Hint 3

```
test_plain_palindrome: 'level' -> True
test_plain_non_palindrome: 'python' -> False
test_ignores_case: 'Level' -> True
test_ignores_spaces: 'nurses run' -> True
test_not_only_ends: 'abca' -> False
test_empty_and_single: '' -> True, 'x' -> True
test_two_letters: 'ab' -> False
```
