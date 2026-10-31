## Hint 1

`Pair` has two type placeholders, so it inherits from `Generic[A, B]`. The order in the brackets matters: `Pair[str, int]` means `A = str`, `B = int`. If `swap` exchanges the values, what does it do to the order of the placeholders in the return hint?

## Hint 2

`map_first` takes a function from `A` to some new type `C`, and the new pair has `C` in the first place and still `B` in the second: `Pair[C, B]`. Which one is it for `map_second`? Remember `frozen=True`: you cannot change `self`, so every method builds and returns a new `Pair`.

## Hint 3

```
@dataclass(frozen=True)
class Pair(Generic[A, B]):
    first: A
    second: B
    swap(self) -> "Pair[B, A]":                  return Pair(self.second, self.first)
    map_first(self, func: Callable[[A], C]) -> "Pair[C, B]":  return Pair(func(self.first), self.second)
    map_second(self, func: Callable[[B], C]) -> "Pair[A, C]": return Pair(self.first, func(self.second))

def swap_tuple(p: tuple[A, B]) -> tuple[B, A]:  a, b = p ; return (b, a)
```
