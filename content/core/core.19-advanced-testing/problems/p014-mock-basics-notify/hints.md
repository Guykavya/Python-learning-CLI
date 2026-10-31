## Hint 1

A `Mock` records every call made to it. After `notify(sender, ...)` runs, which call do you expect on
`sender.send`? With which two arguments? What should it **not** have received for a blank message?

## Hint 2

Give the user a name that differs from the email, so sending to the wrong field is visible. Test the
return value of `notify` separately from what was sent. Which bugs does "sent exactly once" catch?

## Hint 3

```
user = {"name": "Ann", "email": "ann@example.com"}
test_sends_prefixed_text:  notify(Mock(), user, "hi") -> True; send called once with (email, "[notice] hi")
test_strips_spaces:        message "  hi  " -> sent text "[notice] hi"
test_blank_sends_nothing:  for "" and "   ": result False, sender.send.assert_not_called()
test_returns_true_when_sent
```
