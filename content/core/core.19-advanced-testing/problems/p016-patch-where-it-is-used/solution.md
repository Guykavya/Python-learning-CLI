## Approach

`from clock import now` copies a reference to the function into the importing module's namespace as
`app_greet.now`. Patching `clock.now` replaces the attribute in module `clock`, but `app_greet`
still holds the old function, so the patch has no effect. Patch `app_greet.now` instead.

With `import clock` the code looks the function up in `clock` every time (`clock.now()`), so patching
`clock.now` works (and so does `app_stamp.clock.now`, which is the same attribute). The same logic
gives `app_files.exists` and `app_mail.Mailer`.

## Code

```python
def targets():
    return {
        "greeting": "app_greet.now",
        "stamp": "clock.now",
        "has_config": "app_files.exists",
        "welcome": "app_mail.Mailer",
    }
```

## Complexity

Not applicable.

## Another way

Avoid the question: pass the clock, the existence check or the mailer **in** as arguments
(dependency injection, the next problems). Then there is nothing to patch.
