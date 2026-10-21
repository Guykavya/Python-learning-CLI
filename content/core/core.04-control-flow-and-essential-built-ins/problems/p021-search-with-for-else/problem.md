# Search a sentence with for-else

Read a target word on the first line and a sentence on the second line. Find the **first**
word of the sentence that equals the target, ignoring capital letters and ignoring the
punctuation characters `.,!?` at either end of the sentence word.

- Found: print `Found '<target>' as word N`, where `N` counts from 1.
- Not found: print `'<target>' not found`.

Print the target as it was typed (stripped of spaces).

**Example**

Input:
```
cat
The Cat sat. The cat ran!
```
Output:
```
Found 'cat' as word 2
```

**Rule for this problem:** use a `for` loop with an `else` clause for the "not found" case.
No flag variable is needed. The tests check that your loop has an `else`.
