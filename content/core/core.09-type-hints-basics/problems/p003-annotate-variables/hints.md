## Hint 1

A variable hint is a colon and a type between the name and the `=`. What type is `0`? What is the type of a list that will hold strings?

## Hint 2

For the collections, put the type of the **contents** in square brackets: `list[str]`, `dict[str, int]`. For the pair of numbers, a tuple with a fixed shape needs one type per position. For "text or nothing", use `|`.

## Hint 3

```
count: int = 0
price: float = 9.5
title: str = "Report"
tags: list[str] = []
stock: dict[str, int] = {}
origin: tuple[int, int] = (0, 0)
nickname: str | None = None
```
