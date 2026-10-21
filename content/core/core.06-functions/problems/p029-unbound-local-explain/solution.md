See the model answer shown when you check. The ideas that must appear:

1. Reading an unassigned name falls through LEGB to the global.
2. Any assignment in the body makes the name local for the whole body, decided at compile time.
3. `record.__code__.co_varnames` shows `('visits',)`.
4. Preferred fix: pass the value in and return the new one; `global` works but hides state.
5. Mutating a global list needs no `global`, because the name is not rebound.
