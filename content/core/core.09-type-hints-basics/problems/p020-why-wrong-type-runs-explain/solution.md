See the model answer shown when you check. The ideas that must appear:

1. The interpreter stores the hints (in `__annotations__`) and never checks them. Calls are not validated.
2. `"3" * 4` is string repetition, which is legal, so the body runs and returns `"3333"`. A silent wrong answer travels on; a crash would at least point at the problem.
3. A **static** checker such as mypy rejects `area("3", 4)` (`[arg-type]`) when you run it, **before** the program runs. It reads the code and does not execute it. It is not the interpreter, and it only helps if you run it.
4. Add an explicit `isinstance` check that raises `TypeError`. It belongs at the boundary where data enters the program (input, files, network); inside, between annotated functions, mypy is enough.
