## Hint 1

Which of the three functions allows the same element twice? Which of them cares about order? Write the three results for `"abc"`, `k = 2` by hand first: `aa ab ac ba bb bc ca cb cc`...

## Hint 2

`product` takes `repeat=k`. The other two take `k` as a second argument. To count a lazy iterator without storing it, add 1 for each item.

## Hint 3

```
return {
  "product": sum(1 for _ in product(items, repeat=k)),
  "permutations": sum(1 for _ in permutations(items, k)),
  "combinations": sum(1 for _ in combinations(items, k)),
}
```
