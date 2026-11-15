# A calculator with brackets and unary minus

Write `calculate(s)` that evaluates an arithmetic expression given as a string and returns an `int`. The expression can contain:

- non-negative integers (several digits);
- the operators `+ - * /` with the usual precedence (`*` and `/` before `+` and `-`; equal precedence left to right);
- brackets `(` and `)`, nested to any depth up to 100;
- spaces anywhere between tokens;
- **unary minus**: a `-` at the very start of the expression or right after a `(`, as in `-5`, `-(2+3)` or `(-4*2)`. It is never written twice in a row (`--5` does not appear) and never right after another operator (`2*-5` does not appear).

**Division truncates toward zero**: `7/2` is `3` and `-7/2` is `-3` (not Python's `-4`). No division by zero occurs. Do not use `eval`.

The chapter shows two calculators (section 6, "Evaluate with a single pass"): one for `+ -` with brackets, one for `+ - * /` without brackets. This problem needs both ideas at once.

## Example

```python
>>> calculate("2-(5-6)")
3
>>> calculate(" 3 + 5 / 2 ")
5
>>> calculate("-(2+3)*4")
-20
>>> calculate("2*(5+5*2)/3+(6/2+8)")
21
>>> calculate("(-7)/2")
-3
>>> calculate("10 - (-3)")
13
```

## How it is tested

Fixed examples, then 1,500 random expressions built from a random expression tree. The tree is evaluated with truncating division to get the true value; for the expressions without `/`, the test also checks that Python's `eval` agrees, so the generated strings mean what they should.

## Constraints

- `1 <= len(s) <= 10**4`.

## Think about

A `(` starts a smaller expression of exactly the same shape. If you had a function that evaluates "an expression up to its closing `)`", what would it do when it meets a `(`?
