See the model answer shown when you check. The ideas that must appear:

1. A bare name is a capture pattern: it matches anything and binds the subject to that name.
2. An irrefutable capture before other cases makes them unreachable, so Python raises `SyntaxError: name capture 'YES' makes remaining patterns unreachable`.
3. In the "fixed" version `case YES:` matches every answer and rebinds `YES` to the answer.
4. Dotted names (`Answers.YES`, `module.NAME`) are value patterns compared with `==`; bare names capture.
5. Fixes: literals (`case "y":`), dotted constants, a guard (`case a if a == YES:`), or `if`/`elif`.
6. Capturing is the core feature of patterns (`case ["go", direction]:`); bare names must capture or destructuring would be ambiguous.
