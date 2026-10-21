# find, count and the empty string

Predict **exactly** what this program prints, one line per `print`. Do not run it until you have written your answer.

```python
s = "a-b-c"
print(s.find("-"))
print(s.rfind("-"))
print(s.find("-", 2))
print(s.find("x"))
print(s[s.find("x")])
print(s.find(""))
print(s.rfind(""))
print(s.count(""))
print(s.count("-", 0, 2))
print("" in s, "" in "")
print(s.partition("x"))
print(s.rpartition("-"))
```

Write your answer in `answer.txt`, one line per printed line.
