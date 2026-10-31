## Approach

Judge inheritance by the promise it makes, not by how much typing it saves. A subclass must work
everywhere its parent works (chapter section 14, "composition vs inheritance", and the `Stack(list)`
leak in section 21). A stack does **not** allow what a list allows, so it should **have** a list, not
**be** one. Composition gives you a small public interface that you control, and you delegate the real
work to the list inside.

## Model answer

See `answer.md` for the model answer.

## Complexity

All five operations of the composed `Stack` are O(1), the same as on the list underneath.

## Another way

Try it: write both versions in the REPL and compare `[n for n in dir(s) if not n.startswith("_")]`: `Stack(list)` shows the eleven list
methods plus your three; the composed one shows only your five. Then write a test for the composed version that checks
`not hasattr(Stack(), "insert")`. With a bigger interface it is also common to inherit from an
**abstract** base that describes only what you want (chapter section 16), instead of a concrete class
like `list`.
