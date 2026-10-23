## Hint 1

The error case first: what should happen for `average([])`? Write `with pytest.raises(ValueError): average([])` and run it.

## Hint 2

`ZeroDivisionError` is not a `ValueError`, so a function that forgets the check will make this test fail by itself. What does `match="empty"` add? A function that raises `ValueError("bad")`.

## Hint 3

```
test_simple_list: average([2, 4, 6]) == 4
test_result_is_not_rounded_down: average([1, 2]) == 1.5
test_single_number: average([7]) == 7
test_negative_numbers: average([-2, 2, 10]) ...
test_empty_list_raises: with pytest.raises(ValueError, match="empty")
```
