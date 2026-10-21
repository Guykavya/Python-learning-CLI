- `input("Name: ")`: the prompt text is printed, so the first line of output is
  no longer the border.
- `print("Name   : ", name)`: the label already ends with a space and `print`
  adds another, giving two spaces.
- Converting the year with `int(input())` and then `"Year   : " + year`, which
  raises `TypeError`.
- Counting the dashes wrong. Build them with `"-" * 20`.
