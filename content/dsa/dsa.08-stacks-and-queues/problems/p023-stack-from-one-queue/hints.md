## Hint 1

Keep the queue in "stack order": the newest item at the front. After `append(x)` the new item is at the back. Moving one item from the front to the back is `q.append(q.popleft())`. How many times must you do that?

## Hint 2

```
__init__: self.q = queue_factory()
push(x):  self.q.append(x)
          repeat len(self.q) - 1 times: self.q.append(self.q.popleft())
pop():    return self.q.popleft()
top():    return self.q[0]
empty():  return not self.q
```
