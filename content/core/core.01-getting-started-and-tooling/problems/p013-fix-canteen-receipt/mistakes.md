- Fixing the TypeError by making `quantity = "3"`. Now `price * quantity` is
  `"333...` (a string repeated 15 times), and the total line breaks.
- Replacing `totl` with `45`. It hides the bug and gives wrong receipts when
  the price changes.
- Expecting all three errors to be reported at once. Python stops at the first
  one.
- Writing `"Quantity: " + str(quantity)` but also keeping a space in the label,
  giving `Quantity:  3`.
