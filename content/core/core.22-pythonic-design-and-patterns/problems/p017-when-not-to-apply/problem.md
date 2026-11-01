# Explain: when NOT to apply the pattern

Design patterns solve real problems, but copied from a Java book into Python they often become
ceremony. Four snippets follow. For **each one** write:

1. the problem the design *claims* to solve,
2. why Python does not need it here,
3. the simple version (a few lines of code is fine),
4. **one situation** where the heavier design would be worth it.

**Snippet A: the factory of factories**

```python
class AbstractGreeterFactoryFactory:
    def create_factory(self, language):
        return GreeterFactory(language)

class GreeterFactory:
    def __init__(self, language):
        self.language = language
    def create(self):
        return Greeter(self.language)

class Greeter:
    def __init__(self, language):
        self.language = language
    def greet(self, name):
        return ("Hello, " if self.language == "en" else "Hola, ") + name
```

**Snippet B: four base classes for one method**

```python
class Saver(ABC):
    @abstractmethod
    def save(self, data): ...

class Validator(ABC):
    @abstractmethod
    def validate(self, data): ...

class Logger(ABC):
    @abstractmethod
    def log(self, msg): ...

class Notifier(ABC):
    @abstractmethod
    def notify(self, msg): ...

class UserService(Saver, Validator, Logger, Notifier):
    def save(self, data): ...
    def validate(self, data): ...
    def log(self, msg): ...
    def notify(self, msg): ...
```

**Snippet C: the classic Singleton**

```python
class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.values = {}
        return cls._instance
```

**Snippet D: a strategy class for `len`**

```python
class LengthStrategy:
    def measure(self, items):
        return len(items)

class Measurer:
    def __init__(self, strategy):
        self.strategy = strategy
    def run(self, items):
        return self.strategy.measure(items)
```

Write `answer.md` (about 300 to 400 words, four short parts, A to D).

**Example of the level of detail expected (a different snippet)**

> *`class Adder: def add(self, a, b): return a + b`, used as `Adder().add(1, 2)`.* It claims
> to group behavior, but it has no state, so a plain function `def add(a, b)` does the same job
> with no object to create. A class would be worth it once several adders share configuration
> (for example a rounding mode) that must live together.
