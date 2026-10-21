## Hint 1

List the shapes of input: size divides the length, size does not divide the length, size bigger than the list, size 1, empty list. A test for each shape.

## Hint 2

A bug that damages the *argument* is invisible if you only look at the result. After calling `chunk(data, 2)`, what should `data` still be?

## Hint 3

```
test_exact_division, test_last_piece_is_shorter, test_size_bigger_than_list, test_empty_list_gives_no_pieces
test_pieces_are_lists, test_input_is_not_changed (data = [...]; chunk(data, 2); assert data == [...])
test_bad_size_raises: with pytest.raises(ValueError, match="positive") for 0 and -1
```
