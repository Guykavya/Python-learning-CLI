## Hint 1

Write the ready queue down on paper and update it at every pause. After the two
`create_task` lines it is `[A, B]`, and `main` is still running. What does the queue look
like after `main` reaches `await asyncio.sleep(0)`?

## Hint 2

Use this format, one row per turn (the task at the front runs until its next pause):

```
queue before      runs   prints                  pauses at         queue after
[A, B, main]      A      A step 0                sleep(0)          [B, main, A]
[B, main, A]      B      B step 0                sleep(0)          [main, A, B]
[main, A, B]      main   main after sleep(0)     await t1 (waits)  [A, B]
...
```

When A returns, `main` (waiting for `t1`) joins the **end** of the queue: is B already in
front of it?
