# Reverse words two ways

Read one line. Print two lines:

1. the words in **reverse order**, separated by single spaces
2. the words in their **original order**, but each word spelled backwards

**Example**

Input `I love Python`. Output:

```
Python love I
I evol nohtyP
```

Extra spaces between words in the input do not matter: words are what `split()` gives. If
the line has no words, print `(nothing)`.

Use `reversed()` for both jobs.
