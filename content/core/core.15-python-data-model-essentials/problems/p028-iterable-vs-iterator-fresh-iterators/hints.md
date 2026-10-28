## Hint 1

Run `iter(c) is c` and `iter(r) is r` in your head (or the REPL). What does each give? What does that tell you about where the position of the countdown is kept?

## Hint 2

```
1. iterable: __iter__ -> iterator ; iterator: __next__ (+ __iter__ returning self); for = iter() once, next() until StopIteration
2. CountDown is its own iterator -> state lives in self.n -> used up after one pass
3. Range3.__iter__ is a generator function -> new generator (new state) per call
4. __iter__ returns a NEW iterator (generator or helper class) each time
5. containers: iterable (fresh iterator each time) ; streams/files/generators: iterator (one pass)
```
