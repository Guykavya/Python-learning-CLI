See the model answer shown when you check. The ideas that must appear:

1. `orders.py:5` is the file and line of the problem (the call). `Argument 2` is the second argument written in the call. `"str"` is the type that was given, `"float"` is the type the hint expects. `[arg-type]` is the error category: a wrong argument type.
2. The mistake is in the **call**: the function is fine, and a tax rate is a number. Change `"0.18"` to `0.18` (or convert with `float(text)` if the text comes from outside).
3. Python does not check hints, so the program runs until `1 + "0.18"` raises `TypeError`. The message is about `+`, not about the hint.
4. mypy found it without running the code, pointing at the exact bad call, even if the call is on a path that is rarely executed.
