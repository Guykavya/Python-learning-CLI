See the model answer shown when you check. The ideas that must appear:

1. The lambdas close over one shared variable `label`, not over its value at creation time.
2. The lookup happens when each lambda is called (late binding), after the loop ended on 'Quit'.
3. `def` in the loop behaves the same; the problem is closures, not lambda.
4. Fix 1: `lambda label=label: ...` works because defaults are evaluated when the function is created.
5. Fix 2: a factory function gives each closure its own new cell.
6. The default-argument fix exposes an overridable parameter; late binding is useful for live values.
