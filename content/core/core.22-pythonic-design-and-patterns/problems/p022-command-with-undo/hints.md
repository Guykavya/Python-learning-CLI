## Hint 1

What does each command need to remember so it can reverse itself? `Insert` knows what it added
and where. What about `Delete` and `Replace`, whose old text is only known when they run? Where
should that be saved, in `__init__` or in `do()`?

For `History`: when you undo, where should the command go so that `redo` can find it? When
should that second place be emptied?

## Hint 2

```
class Delete:
    __init__: store editor, start, end; removed = ""
    do():  check range (IndexError) FIRST; removed = text[start:end]; text = text[:start] + text[end:]
    undo(): text = text[:start] + removed + text[start:]

class Macro:
    do():  done = []
           try: for c in commands: c.do(); done.append(c)
           except: for c in reversed(done): c.undo();  raise
    undo(): for c in reversed(commands): c.undo()

class History:
    run(c):   c.do(); undo_stack.append(c); redo_stack.clear()
    undo():   if no undo_stack: return False
              c = undo_stack.pop(); c.undo(); redo_stack.append(c); return True
    redo():   mirror image
```

Undo in reverse order is not a style choice: positions in later commands assume the earlier
ones happened.
