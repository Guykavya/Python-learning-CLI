- Writing `(?<=₹|Rs\.)`. Python raises `re.error: look-behind requires fixed-width pattern`.
  Use one lookbehind per width.
- Writing `(?<=₹\s*)`. Also not fixed width.
- Forgetting to escape the dot in `Rs\.`: then `Rs5` or `RsX40` would count.
- Making the decimal part `\.?\d*`. Then `Rs.40.` gives `'40.'`, and the dot at the end of the
  sentence is treated as part of the number.
- Calling `float('1,299.50')` without removing the commas: `ValueError`.
- Using a capturing group like `(₹|Rs\.)` together with the number. `findall` then returns the
  group, not the number.
