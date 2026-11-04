# Group the anagrams

You get `n` lower-case words. Group the words that are anagrams of each other. The idea: give every word a **canonical
key** that is the same for all anagrams, for example its letters in sorted order. Words with the same key go in the
same group.

Print one line per group. Inside a group list the words in **alphabetical order** (repeats stay, listed each time). Print
the groups ordered by their **first (smallest) word**.

## Input

- Line 1: `n`.
- Line 2: `n` words separated by spaces.

## Output

One line per group, words separated by single spaces.

## Example

Input:

```
6
eat tea tan ate nat bat
```

Output:

```
ate eat tea
bat
nat tan
```

`eat`, `tea`, `ate` all sort to `aet`. `tan` and `nat` sort to `ant`. `bat` is alone.

## Constraints

- `1 <= n <= 100000`
- Each word has 1 to 10 letters from `a` to `z`.
