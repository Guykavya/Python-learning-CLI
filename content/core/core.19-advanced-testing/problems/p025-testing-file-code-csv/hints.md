## Hint 1

Write down the interesting file contents: two rows of one category; the same category written in
different cases or with spaces; a blank amount; an amount of `0`; two amounts such as `0.1` and `0.2`;
only a header. What should each give?

## Hint 2

One helper that writes text to `tmp_path / "data.csv"` and calls `summarise` keeps each test short.
Then a `parametrize` table of `(file_text, expected_dict)` rows covers most bugs. The missing file
needs `pytest.raises(FileNotFoundError)` with a path that was never created.

## Hint 3

```
cases: "food,10 / food,5" -> {"food": 15.0}            (sum, not last value, not row count)
       "Food,1 / food,2 / ' FOOD ',3" -> {"food": 6.0}  (case + strip)
       "food,  " (blank) + "rent,0" -> {"rent": 0.0}   (blank skipped, zero kept)
       "x,0.1 / x,0.2" -> {"x": 0.3}                    (rounding)
       header only -> {}
missing: summarise(tmp_path / "nope.csv") raises FileNotFoundError
```
