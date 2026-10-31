## Hint 1

Type `dir(list)` in the REPL and look at the names without a leading underscore. A `Stack` that inherits from `list` offers
**all** of them. For each line of the program, ask: is this push, pop or peek at the **top**? If not,
why can a stack user do it?

## Hint 2

Inheritance means "can be used wherever the parent is expected". Think of a function
`def tidy(items: list): items.sort()`. Should it be allowed to receive the undo history? What does
`isinstance(s, list)` tell that function?

## Hint 3

Plan of the answer:

```text
1. leaks: insert, sort, s[i] = ..., pop(0), remove, del, reverse, clear, slicing, + returns list
2. is-a (substitutable) vs has-a; a stack forbids what a list allows
3. class Stack: self._items = [] ; push/pop/peek/is_empty/size delegate; IndexError on empty
4. lose: a few free methods; gain: small interface, cannot be misused, inside can change
5. good inheritance: exception hierarchies, Dog(Animal); test = "works everywhere the parent works?"
```
