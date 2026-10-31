## Hint 1

Look at the first line of each module. After `from clock import now`, does `app_greet` still look
up `clock.now` when `greeting()` runs, or does it look up its **own** name `now`?

## Hint 2

Use this rule: patch the name in the module where it is looked up. With `import clock` and
`clock.now()` the lookup goes to the module `clock`; with `from clock import now` it goes to the
module that did the import. For `Mailer`, the code uses the name `Mailer` from `app_mail`.

## Hint 3

```
greeting   -> module app_greet, name now
stamp      -> module clock (accessed as clock.now), name now
has_config -> module app_files, name exists
welcome    -> module app_mail, name Mailer
target string = "<module>.<name>"
```
