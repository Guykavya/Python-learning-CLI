# Patch the name where it is used

The most common reason a `patch` "does nothing" is that it patches the right object under the
**wrong name**. `patch("a.b")` replaces the name `b` inside module `a`. What counts is the name the
code under test **looks up** at call time.

Here are four small modules (the checker creates them for you):

```python
# clock.py
def now():
    raise RuntimeError("the real clock was used in a test")

# app_greet.py
from clock import now
def greeting():
    return "morning" if now() < 12 else "afternoon"

# app_stamp.py
import clock
def stamp():
    return "at " + str(clock.now())

# app_files.py
from os.path import exists
def has_config():
    return exists("/home/you/.config/app.toml")

# mailer.py
class Mailer:
    def send(self, to, text):
        raise RuntimeError("a real email was sent in a test")

# app_mail.py
from mailer import Mailer
def welcome(name):
    return Mailer().send(name, "welcome")
```

In `solution.py` write a function `targets()` that returns a dict with four strings, the **patch
targets** that make each function testable:

```python
{"greeting": "...", "stamp": "...", "has_config": "...", "welcome": "..."}
```

`"greeting"` is the string you would pass to `patch(...)` to control `app_greet.greeting()`,
`"stamp"` for `app_stamp.stamp()`, `"has_config"` for `app_files.has_config()`, and `"welcome"` for
`app_mail.welcome()` (replace the whole class `Mailer` by a mock).

The checker really applies your four targets with `patch(target, ...)`, calls the function, and
fails if the real clock, file check or mailer is reached.

**Example** (for a different module `app_x` with `from clock import now`): the target would be
`"app_x.now"`, not `"clock.now"`.
