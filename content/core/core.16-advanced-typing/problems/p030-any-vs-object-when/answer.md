**1. Not the same.** `object` is a real type: the top of the hierarchy. Every value fits into an
`object`, but the checker only lets you do what **all** objects can do (print, compare, `str()`);
to use it as a `str` or an `int` you must narrow it with `isinstance`. `Any` is the opt-out: the
checker stops checking. A value of type `Any` can be passed anywhere, assigned to any variable,
and have any attribute or index used on it, and the result is again `Any`. So `object` is "unknown
and safe", `Any` is "unknown and unchecked".

**2. `log`.** I would use `object`. `log` only prints the value, and everything can be printed, so
it accepts all arguments. If someone later changes the body to `value.strip()`, mypy would
immediately complain with `object`; with `Any` it would stay silent and crash at run time.

**3. `read_config`.** `config` is `Any`, so `config["server"]["port"] + 1` and
`retries: int = config["retries"]` are never checked. If the file has `"port": "8080"` (a string)
then `+ 1` raises `TypeError` at run time, and if `retries` is `"3"` the variable annotated `int`
silently holds a `str`. mypy says nothing. Better: return `object` (or a `TypedDict`/`dict[str,
object]`) and validate or narrow the data in one place, with `isinstance` or a validator, before it
is used.

**4. A fair use of `Any`.** A truly dynamic boundary where a precise type is impractical (a
legacy module you are only starting to annotate, a decorator that really can wrap anything, or
a third party library with no stubs). It is also the right escape hatch while migrating a big
untyped codebase step by step, as long as the `Any` stays at the border and is converted to real
types quickly.
