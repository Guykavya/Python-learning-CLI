# Format specs under the microscope

Predict **exactly** what this program prints, one line per `print`. Do not run it until you have written your answer.

```python
x = 1234.5
n = 42
print(f"[{x:10.1f}]")
print(f"[{x:<10,.2f}]")
print(f"[{n:^7}]")
print(f"[{n:*>6}]")
print(f"[{-n:06}]")
print(f"[{n:+}] [{n: }]")
print(f"{n:b} {n:#o} {n:X}")
print(f"{0.0625:.1%}")
print(f"{x:.2e}")
print(f"[{'format':.3}] [{'ab':>{n // 10}}]")
print(f"{n=}, {x / 10 = :.0f}")
```

Write your answer in `answer.txt`, one line per printed line.
