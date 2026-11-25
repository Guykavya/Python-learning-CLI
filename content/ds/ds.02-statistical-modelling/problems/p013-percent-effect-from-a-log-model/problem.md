# Percent effect from a log model

Chapter section 7.2. In a model `log(y) ~ x`, a coefficient `b` means that `y` is multiplied by `exp(b)`. The shortcut "`100 * b` percent" is only an approximation.

```python
import math

for b in [0.02, 0.10, 0.40, -0.40]:
    shortcut = 100 * b
    exact = 100 * (math.exp(b) - 1)
    print(f"b={b:+.2f}: shortcut {shortcut:+.2f}%  exact {exact:+.2f}%")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

(Values you may use: `exp(0.02) = 1.0202`, `exp(0.10) = 1.10517`, `exp(0.40) = 1.49182`, `exp(-0.40) = 0.67032`.)

## Example

For `b = 0.05` the line would be `b=+0.05: shortcut +5.00%  exact +5.13%`.

## After you answer

- For which of the four values is the shortcut worst? Why does a drop of 40 percent not need a coefficient of -0.40?
