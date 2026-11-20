## Hint 1

Look at each operation of the program and ask what it costs. What is the cost of `queue.pop(0)` when the list holds 200 000 numbers? What does `input()` cost compared with reading everything at once? And `print` inside a loop?

## Hint 2

Three fixes: (1) read all tokens with `sys.stdin.read().split()`; (2) replace the list by `collections.deque` and use `popleft()`; (3) collect the output lines in a list and print them once.

## Hint 3

```text
tokens = read().split(); walk with an index
dq = deque()
"push": dq.append(int(next token))
"pop":  out.append(str(dq.popleft())) if dq else out.append("empty")
"size": out.append(str(len(dq)))
print("\n".join(out))
```

Careful: `push` consumes two tokens (`push` and the number), `pop` and `size` consume one.
