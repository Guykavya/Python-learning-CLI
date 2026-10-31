## Approach

Separate the three symptoms and match each one to its cause: strange first character is the BOM, `ZoÃ«` is a
wrong encoding, and different line ends are newline translation. All three come from things that Python
decides for you when you leave an argument out. The fix is always to say it yourself.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Show it with bytes. Write `b"\xef\xbb\xbfZo\xc3\xab\r\n"` to a file. Read it with `encoding="utf-8"`, then with
`encoding="utf-8-sig"`, then with `encoding="cp1252"`, and print `repr` every time. The three results show
all three problems at once.
