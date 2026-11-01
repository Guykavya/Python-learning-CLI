## Approach

The model answer is in `answer.md`. All four snippets share one idea: a pattern is a *solution to
a pain*. If the pain is absent (no variation, no second implementation, no shared state), the
pattern is only extra code to read. Python removes some pains completely: first-class functions
(strategy, factory), modules (singleton), duck typing (interfaces).

## Check your answer

- Did you say what each design *claims* (not just "it is too complex")?
- Did you name the Python feature that replaces it: function or class as a factory, a module, `Protocol`, a callable parameter?
- Did you show real simple code for each?
- Did you give a **concrete** situation for the heavy version, such as families of objects (A), many plugins (B), exclusive hardware (C), a configured stateful policy (D)?
- Did you avoid saying "patterns are bad"? The point is *when*.

## Another way

Judge any design with three questions: (1) how many implementations exist today? (2) what is
the cost of adding the abstraction later, when the second one appears? (3) who reads this code?
When the answers are "one", "small" and "a new teammate", write the simple version and refactor
when the second implementation arrives.
