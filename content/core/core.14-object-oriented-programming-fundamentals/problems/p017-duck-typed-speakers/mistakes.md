- Wrapping the call `thing.speak()` in the `try`. A real bug inside `speak` is then swallowed.
- Checking `isinstance(thing, Duck)`. A `Robot` or `Parrot` can speak too; duck typing does not care
  about the class.
- Using a bare `except:` or `except Exception:`. That hides every error, even typing mistakes.
- Appending `thing.speak` (without brackets). The list then holds method objects, not strings.
- Calling `speak()` twice (once to test, once to collect). Side effects happen twice.
