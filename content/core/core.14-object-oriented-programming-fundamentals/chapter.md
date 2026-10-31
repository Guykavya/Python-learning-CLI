# Chapter 14: Object-oriented programming fundamentals

You have used objects since your first day with Python. A string is an object: `"hello".upper()`. A list is an object: `items.append(3)`. A file and a `Path` are objects too. Each one carries some **data** and offers **methods** that work on that data. Until now, other people made all these objects. In this chapter you make your own.

A **class** is a blueprint for a new kind of object. You decide what data each object holds and what it can do. With classes you can describe the things in your problem directly: a `Book`, a `Member`, a `Loan`, a `Library`. Your code then reads like the problem, not like a pile of dictionaries.

The chapter has four parts:

- **Building classes** (sections 1 to 9): classes, instances, `self`, `__init__`, class attributes, `classmethod` and `staticmethod`, private names, properties, and how Python finds an attribute.
- **Relating classes** (sections 10 to 16): inheritance, `super()`, multiple inheritance and the **MRO**, mixins, composition, duck typing and abstract base classes.
- **Errors as classes** (sections 17 to 19): your own exception classes, chaining with `raise ... from ...`, and exception groups with `except*`.
- **The project** (section 20): designing a small library management system with its own exceptions.

By the end you reach the three outcomes of the module:

- You can **model a real domain with classes** and decide between **composition and inheritance**.
- You can **design a custom exception hierarchy** for a library.
- You can **predict the MRO** of a diamond inheritance on paper.

Along the way you will answer questions like these: What is `self`, and why must you write it? Why does a list stored on the class change for every object? Is there "private" in Python? What does `super()` really call (hint: not always the parent)? When should a class *have* another object instead of *being* a kind of it? What is the difference between "The above exception was the direct cause" and "During handling of the above exception"?

**A note on how examples are shown.** Every block of code is followed by the exact output produced by really running it with **Python 3.14** on Linux. Some outputs contain **memory addresses**, such as `<__main__.Dog object at 0x7f3a1c2b4e00>`. These numbers are **machine-specific**: they change on every run and on every computer. Only the shape matters. Tracebacks are shown as Python printed them, but the `File "...", line N` lines and the source lines under them are **trimmed** and replaced by `...`, so you can focus on the error itself.

**How to read this chapter.** Type the examples and run them. For each **Predict the output** exercise, decide what Python will print and write it down *before* you open the answer. Being wrong is useful: it shows you exactly which rule you have not understood yet.

What this chapter leaves out on purpose: making your objects work with `+`, `==`, `<`, `len()`, `[]` and `with` is the **data model**, in **core.15**. Here you meet only a simple `__repr__` (and `__str__`) so that printing an object shows something useful. Dataclasses and `enum` also come later.

## Table of contents

1. [Why classes](#1-why-classes)
2. [Your first class](#2-your-first-class)
3. [`self` and bound methods](#3-self-and-bound-methods)
4. [`__init__` and object construction](#4-__init__-and-object-construction)
5. [Class attributes vs instance attributes](#5-class-attributes-vs-instance-attributes)
6. [`classmethod` and `staticmethod`](#6-classmethod-and-staticmethod)
7. [Encapsulation conventions and name mangling](#7-encapsulation-conventions-and-name-mangling)
8. [Properties](#8-properties)
9. [How attribute lookup really works](#9-how-attribute-lookup-really-works)
10. [Inheritance and overriding](#10-inheritance-and-overriding)
11. [`super()` in single inheritance](#11-super-in-single-inheritance)
12. [Multiple inheritance and the MRO](#12-multiple-inheritance-and-the-mro)
13. [Mixins](#13-mixins)
14. [Composition vs inheritance](#14-composition-vs-inheritance)
15. [Polymorphism and duck typing](#15-polymorphism-and-duck-typing)
16. [Abstract base classes](#16-abstract-base-classes)
17. [Custom exception classes and hierarchies](#17-custom-exception-classes-and-hierarchies)
18. [Exception chaining](#18-exception-chaining)
19. [Exception groups and `except*`](#19-exception-groups-and-except)
20. [Project: a library management system](#20-project-a-library-management-system)
21. [Common traps](#21-common-traps)
22. [Summary](#22-summary)

## 1. Why classes

### 1.1 The problem: data and code drift apart

Here is a tiny program about water tanks, **without classes**. A tank is a dictionary, and the operations are functions that take the dictionary.

```python
def make_tank(name, capacity):
    return {"name": name, "capacity": capacity, "litres": 0}

def fill(tank, litres):
    if litres <= 0 or tank["litres"] + litres > tank["capacity"]:
        raise ValueError("bad amount")
    tank["litres"] += litres

t = make_tank("roof", 500)
fill(t, 120)
print(t)
```
```text
{'name': 'roof', 'capacity': 500, 'litres': 120}
```

This works while the program is small. As it grows, problems appear:

- **Nothing protects the data.** Any code can write `t["litres"] = 9000`, or `t["litre"] = 10` (a typo silently creates a new key). The rule "never more than the capacity" lives in `fill`, but nobody is forced to use `fill`.
- **Data and functions are separate.** To find every function that works on a tank, you search the whole program. Nothing stops `fill(order, 5)` on an order dictionary.
- **Names collide.** A fuel tank needs a different `fill`. Soon you have `fill_water`, `fill_fuel`, and `if tank["type"] == ...` everywhere.

### 1.2 The idea: bundle data with the code that works on it

A class puts the data and the functions that work on it **in one place**. Here is the same program with a class. Sections 2 to 4 explain every line.

```python
class Tank:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.litres = 0

    def fill(self, litres):
        if litres <= 0 or self.litres + litres > self.capacity:
            raise ValueError("bad amount")
        self.litres += litres

t = Tank("roof", 500)
t.fill(120)
print(t.name, t.litres)
print(type(t))
```
```text
roof 120
<class '__main__.Tank'>
```

`Tank` is a **new type**: `type(t)` says `Tank`, just like `type("hi")` says `str`. The operations are **methods**: `t.fill(120)` instead of `fill(t, 120)`. Another class, `Order`, can have its own `fill` without any collision. And later a `FuelTank` can **reuse** `Tank` and change only what is different (section 10).

### 1.3 Words you will meet

| Word | Meaning | Example |
|---|---|---|
| **class** | a blueprint for a kind of object | `Tank` |
| **instance** (object) | one object made from a class | `t = Tank("roof", 500)` |
| **attribute** | a name stored on an object | `t.litres` |
| **method** | a function defined in a class | `t.fill(120)` |
| **inheritance** | a class built on top of another class | `class FuelTank(Tank)` |

"Object-oriented programming" (OOP) means organising a program around such objects. It is a tool, not a rule for everything. A small script with three functions does not need classes. A program with many kinds of things, each with data and rules, usually does.

## 2. Your first class

### 2.1 The `class` statement

```python
class Dog:
    pass

d1 = Dog()
d2 = Dog()
print(type(d1))
print(d1 is d2, isinstance(d1, Dog))
print(d1)
```
```text
<class '__main__.Dog'>
False True
<__main__.Dog object at 0x72d954160ad0>
```

- `class Dog:` creates a class and binds it to the name `Dog`. Class names use **CapWords**: `Dog`, `BankAccount`, `HttpError`. Functions and variables use `snake_case`.
- `Dog()` **calls** the class, and calling a class makes a **new instance**. `d1` and `d2` are two different objects.
- `__main__.Dog` means "the class `Dog` from the module running as the main program" (core.13).
- The last line is the default way an object prints: its class and its memory address (machine-specific). Section 4.4 shows how to print something useful.

### 2.2 Attributes: names stored on an object

You create an attribute by assigning to `object.name`:

```python
class Dog:
    pass

rex = Dog()
rex.name = "Rex"
rex.age = 3
fido = Dog()
fido.name = "Fido"
print(rex.name, rex.age, fido.name)
print(vars(rex))
print(vars(fido))
```
```text
Rex 3 Fido
{'name': 'Rex', 'age': 3}
{'name': 'Fido'}
```

Each instance has its own storage, a dictionary called `__dict__`. The built-in `vars(obj)` returns it. `rex` has `name` and `age`; `fido` has only `name`. Asking for a missing attribute raises `AttributeError`:

```python
print(fido.age)
```
```text
Traceback (most recent call last):
  ...
AttributeError: 'Dog' object has no attribute 'age'
```

Adding attributes from outside like this is possible, but it is a bad habit: nothing guarantees that every `Dog` has a `name`. Section 4 shows the proper way.

### 2.3 Methods: functions inside the class

A **method** is a function defined inside the class body. Its first parameter is the instance it works on. By a very strong convention, this parameter is called `self`.

```python
class Dog:
    def bark(self):
        return f"{self.name} says woof"

    def birthday(self):
        self.age += 1

rex = Dog()
rex.name = "Rex"
rex.age = 3
print(rex.bark())
rex.birthday()
rex.birthday()
print(rex.age)
```
```text
Rex says woof
5
```

You call `rex.bark()` with **no** argument, but `bark` has one parameter, `self`. Python fills it in: `self` becomes `rex`. Inside the method, `self.name` means "the `name` of the object this method was called on".

### 2.4 Predict the output

```python
class Tally:
    def start(self):
        self.value = 0

    def add(self, n):
        self.value += n
        return self.value

a = Tally()
b = Tally()
a.start()
b.start()
a.add(5)
b.add(1)
print(a.add(2), b.add(2))
print(a.value, b.value)
```

<details><summary>Answer</summary>

```text
7 3
7 3
```

`a` and `b` are separate objects, each with its own `value`. `a` goes 0, 5, 7. `b` goes 0, 1, 3. A method changes only the object it was called on, because `self` is that object. Notice also that calling `add` before `start` would fail: `value` would not exist yet. Section 4 fixes that.
</details>

### 2.5 A class is an object too

In Python, **everything is an object**, including classes and functions. The class `Dog` is an object of type `type`, and the methods are stored in it:

```python
class Dog:
    def bark(self):
        return "woof"

print(type(Dog), Dog.__name__)
print("bark" in vars(Dog), type(vars(Dog)["bark"]))
```
```text
<class 'type'> Dog
True <class 'function'>
```

So `bark` is a normal function, stored in the class's dictionary under the name `"bark"`. Keep this picture in your head: **the class holds the methods, the instance holds the data.** Sections 3, 5 and 9 all follow from it.

## 3. `self` and bound methods

### 3.1 `obj.method(x)` is `Class.method(obj, x)`

There is no magic in `self`. When you write `rex.greet("Fido")`, Python:

1. looks up `greet`: not in `rex.__dict__`, so it finds it in the class `Dog`;
2. sees a function reached **through an instance**, and packs the function and the instance together into a **bound method**;
3. calls the function with the instance as the first argument.

So these two lines do the same thing:

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def greet(self, other):
        return f"{self.name} sniffs {other}"

rex = Dog("Rex")
print(rex.greet("Fido"))
print(Dog.greet(rex, "Fido"))
```
```text
Rex sniffs Fido
Rex sniffs Fido
```

(`__init__` sets `self.name` when the dog is made; section 4 explains it.) `Dog.greet` is the plain function from the class, so you pass the instance yourself. `rex.greet` already has the instance inside it. The function needs **some** name for "the object I was called on", and Python makes you write that name explicitly. `self` is not a keyword (any name would work), but every Python programmer expects `self`, so always use it.

### 3.2 Bound method objects

A bound method is a real object. You can store it and call it later:

```python
m = rex.greet
print(m)
print(m.__self__ is rex, m.__func__ is Dog.greet)
print(m("Tom"))
print(sorted([Dog("Rex"), Dog("Bella")], key=lambda d: d.name)[0].name)
```
```text
<bound method Dog.greet of <__main__.Dog object at 0x774e5fc7cad0>>
True True
Rex sniffs Tom
Bella
```

The first line shows the bound method with the dog inside it (the address is machine-specific). It remembers the instance (`__self__`) and the function (`__func__`). Calling `m("Tom")` calls `Dog.greet(rex, "Tom")`. You can pass bound methods anywhere a function is expected, for example to `map` (core.11).

### 3.3 Forgetting `self`

The most common beginner error is forgetting `self` in the definition:

```python
class Robot:
    def hello():
        return "beep"

Robot().hello()
```
```text
Traceback (most recent call last):
  ...
TypeError: Robot.hello() takes 0 positional arguments but 1 was given
```

"Takes 0 positional arguments but 1 was given": you passed nothing, so where does the "1" come from? It is the instance, which Python always passes first. When a count is **one more than you passed**, think of `self`.

The opposite mistake is forgetting `self.` **inside** a method: writing `name` instead of `self.name`. Then Python looks for a local or global variable `name`, and you get a `NameError` (or, worse, you silently use a global with the same name).

### 3.4 A function stored on an instance is not bound

Binding happens only for functions found **on the class**. A function placed directly on an instance is returned as it is:

```python
class Dog:
    def __init__(self, name):
        self.name = name

def shout(x):
    return f"shout: {x}"

rex = Dog("Rex")
rex.speak = shout
print(rex.speak("hi"))

Dog.speak2 = shout
print(rex.speak2())
```
```text
shout: hi
shout: <__main__.Dog object at 0x7fc2ca580ad0>
```

- `rex.speak` is found in `rex.__dict__`, so it is a plain function: `rex.speak("hi")` calls `shout("hi")`.
- `Dog.speak2` lives on the class. Reached through `rex`, it becomes bound, so `rex.speak2()` calls `shout(rex)`, which prints the object (address machine-specific).

You rarely do either on purpose, but the rule "bind only what comes from the class" explains many surprises. Section 9 builds on it.

### 3.5 Predict the output

```python
class Greeter:
    def __init__(self, word):
        self.word = word

    def greet(self, name):
        return f"{self.word}, {name}!"

g1 = Greeter("Hello")
g2 = Greeter("Namaste")
f = g2.greet
g2.word = "Hi"
print(f("Ravi"))
print(Greeter.greet(g1, "Mira"))
print(g1.greet is g1.greet)
```

<details><summary>Answer</summary>

```text
Hi, Ravi!
Hello, Mira!
False
```

- `f` remembers the **object** `g2`, not a copy of its data. When `f` runs, it reads `g2.word`, which is now `"Hi"`.
- `Greeter.greet(g1, "Mira")` passes `g1` by hand.
- Each time you write `g1.greet`, Python makes a **new** bound method object. Two lookups give two objects, so `is` is `False`.
</details>

## 4. `__init__` and object construction

### 4.1 Why we need `__init__`

In section 2 we set attributes from outside, after the object was created. That allows incomplete objects (a `Tally` without `value`). We want: **every new object is complete and valid from the first moment.** The method `__init__` does that. Python calls it automatically, right after it creates the object.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def manhattan_to(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

p = Point(3, 4)
print(p.x, p.y, vars(p))
print(p.manhattan_to(Point(1, 1)))
```
```text
3 4 {'x': 3, 'y': 4}
5
```

Names that start and end with two underscores, like `__init__`, are called **dunder** ("double underscore") names or **special methods**. You do not call them yourself; Python calls them at the right moment. Core.15 shows many more.

### 4.2 What happens when you call `Point(3, 4)`

1. **Create**: Python makes a new, empty `Point` instance. (A special method called `__new__` does this. You almost never write it; ignore it for this chapter.)
2. **Initialise**: Python calls `Point.__init__(new_object, 3, 4)`. Inside, `self` is the new object, and `self.x = x` stores an attribute on it.
3. The new object becomes the value of the expression `Point(3, 4)`.

`__init__` does not create the object and does not return it; it only **fills it in**. It must return `None` (returning anything else raises `TypeError`). The arguments you pass to the class go to `__init__`, so all the function rules from core.06 apply: defaults, keywords, missing arguments.

```python
q = Point(x=1, y=2)
print(q.x, q.y)
r = Point(5)
```
```text
1 2
Traceback (most recent call last):
  ...
TypeError: Point.__init__() missing 1 required positional argument: 'y'
```

The error names `Point.__init__()`. The instance is passed automatically, so only `x` and `y` count.

### 4.3 Validate in `__init__`

`__init__` runs for every new object, so it is the right place to **check the arguments**. If they are bad, raise an exception, and a bad object never exists.

```python
class Booking:
    def __init__(self, guest, nights=1):
        if not guest:
            raise ValueError("guest must not be empty")
        if nights < 1:
            raise ValueError(f"nights must be at least 1: {nights}")
        self.guest = guest
        self.nights = nights
        self.extras = []

ok = Booking("Asha")
print(ok.guest, ok.nights, ok.extras)
try:
    Booking("Ravi", 0)
except ValueError as e:
    print("refused:", e)
```
```text
Asha 1 []
refused: nights must be at least 1: 0
```

Three good habits:

- **Set every attribute in `__init__`**, even if it starts empty (`self.extras = []`). A reader sees all the attributes in one place, and methods can rely on them.
- **Use defaults** for optional arguments (`nights=1`).
- **Never use a mutable default** such as `extras=[]` in the parameter list. As you learned in core.06, that list is created once and shared by all calls. Use `None` and create the list inside.

Keep `__init__` simple: it prepares the object. Reading big files or opening network connections in `__init__` makes objects slow and hard to test.

### 4.4 A simple `__repr__` so printing is useful

The default `<__main__.Point object at 0x...>` does not help when you debug. Python calls the special method `__repr__` to get the "developer" text of an object. You can define it; it must **return a string**:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"

p = Point(3, 4)
print(p)
print([p, Point(0, 0)])
print(f"at {p}")
```
```text
Point(3, 4)
[Point(3, 4), Point(0, 0)]
at Point(3, 4)
```

Good habit: make `__repr__` look like the code that creates the object. The `!r` in the f-string uses `repr()` of each value, so a string shows with quotes.

There is also `__str__`, the "user-friendly" text that `print()` and `str()` use. If a class has no `__str__`, Python uses `__repr__`. If it has both:

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __repr__(self):
        return f"Temperature({self.celsius!r})"

    def __str__(self):
        return f"{self.celsius} °C"

t = Temperature(21.5)
print(t, repr(t), [t])
```
```text
21.5 °C Temperature(21.5) [Temperature(21.5)]
```

A **list** prints its items with `repr`, not `str`. That is why you write `__repr__` first. That is all you need for now; core.15 tells the full story.


## 5. Class attributes vs instance attributes

### 5.1 Two places to store a name

An attribute can live in two places:

- On the **instance**, in its `__dict__`. Each object has its own value. You create these with `self.name = ...`, usually in `__init__`.
- On the **class**. **All instances share** one value. You create these by assigning in the class body, outside any method.

```python
class Pizza:
    size_cm = 30                 # class attribute: shared

    def __init__(self, name):
        self.name = name         # instance attribute: one per pizza

a = Pizza("Margherita")
b = Pizza("Paneer")
print(a.name, b.name)
print(a.size_cm, b.size_cm, Pizza.size_cm)
print(vars(a), "size_cm" in vars(Pizza))
```
```text
Margherita Paneer
30 30 30
{'name': 'Margherita'} True
```

`vars(a)` contains only `name`, yet `a.size_cm` works, because of the **lookup rule for reading** `obj.name`:

1. look in the instance's own `__dict__`;
2. if not found, look in the class (and, as section 10 shows, its parent classes);
3. if still not found, raise `AttributeError`.

This is the same rule that finds methods: methods are simply class attributes that happen to be functions. Class attributes are good for **constants** that belong to the class (`Account.MAX_WITHDRAWAL`), **defaults** that an instance may override, and **data about the class as a whole**, such as a counter.

### 5.2 Assignment always writes to the instance

Here is the rule that surprises people. **Assigning** `obj.name = value` **always writes into the instance's `__dict__`**. It never changes the class attribute. The new instance attribute **shadows** (hides) the class attribute for that one object.

```python
a.size_cm = 40           # creates an instance attribute on a only
print(a.size_cm, b.size_cm, Pizza.size_cm, vars(a))
Pizza.size_cm = 25       # changes the class attribute
print(a.size_cm, b.size_cm, Pizza.size_cm)
del a.size_cm            # remove the shadow
print(a.size_cm)
```
```text
40 30 30 {'name': 'Margherita', 'size_cm': 40}
40 25 25
25
```

`b` has no own value, so it always sees the class value. `a`'s own value hid the class value until we deleted it. To change a class attribute, assign through the **class**: `Pizza.size_cm = 25`, or `type(self).size_cm = 25` inside a method.

### 5.3 Counting instances

A classic use: count the objects and give each one a number.

```python
class Order:
    created = 0

    def __init__(self, customer):
        Order.created += 1
        self.number = Order.created
        self.customer = customer

o1, o2, o3 = Order("Asha"), Order("Ravi"), Order("Asha")
print(o1.number, o2.number, o3.number, Order.created)
```
```text
1 2 3 3
```

Why `Order.created += 1` and not `self.created += 1`? Apply the rules. `self.created += 1` means `self.created = self.created + 1`. The right side **reads** `created` (found on the class: 0). The left side **assigns**, which writes to the **instance**. Every order would get its own `created = 1`, and the class counter would stay 0 forever.

### 5.4 The shared mutable class attribute trap

The most famous class-attribute bug uses a **mutable** value such as a list:

```python
class Team:
    members = []                    # BUG: one list for every team

    def __init__(self, name):
        self.name = name

    def join(self, person):
        self.members.append(person)

red = Team("red")
blue = Team("blue")
red.join("Asha")
print(red.members, blue.members)
print(red.members is blue.members is Team.members)
```
```text
['Asha'] ['Asha']
True
```

`self.members.append(person)` does **not** assign to `self.members`. It **reads** `self.members` (found on the class) and changes that list in place. There is only one list, so every team gets every member. Remember: `self.x = ...` creates an instance attribute; `self.x.append(...)` does not. The fix is to create mutable values **per instance**, in `__init__`: `self.members = []`.

Rule of thumb: **class attributes should be immutable** (numbers, strings, tuples) or deliberately shared. Lists, dicts and sets that belong to one object go in `__init__`.

### 5.5 Predict the output

```python
class Player:
    lives = 3
    scores = []

    def __init__(self, name):
        self.name = name

    def die(self):
        self.lives -= 1

    def score(self, points):
        self.scores.append(points)

p = Player("p")
q = Player("q")
p.die()
p.die()
q.score(10)
p.score(5)
Player.lives = 5
print(p.lives, q.lives)
print(p.scores, q.scores)
print(sorted(vars(p)), sorted(vars(q)))
```

<details><summary>Answer</summary>

```text
1 5
[10, 5] [10, 5]
['lives', 'name'] ['name']
```

- `p.die()` reads `lives` from the class (3) and assigns 2 to `p`. The second call makes it 1. `p` now has its own `lives`, so `Player.lives = 5` does not affect it. `q` never died, so it reads the class value: 5.
- `scores` is one shared list: both players appended to it.
- `p.__dict__` has `lives` and `name`; `q.__dict__` has only `name`.
</details>

## 6. `classmethod` and `staticmethod`

### 6.1 Three kinds of methods

Some methods do not need an instance:

| Kind | Decorator | First argument | Use it for |
|---|---|---|---|
| instance method | none | `self`, the instance | almost everything |
| class method | `@classmethod` | `cls`, the class | alternative constructors, class-level data |
| static method | `@staticmethod` | nothing special | a helper that belongs with the class but needs neither |

You know decorators from core.11. These two are built in, and they change what the method receives.

### 6.2 Alternative constructors with `@classmethod`

A class has only one `__init__`, but you often want several ways to create an object: from numbers, from a string, from a dictionary read from JSON. A class method receives the **class** as `cls` and can call `cls(...)`:

```python
class Duration:
    def __init__(self, minutes, seconds):
        self.minutes = minutes
        self.seconds = seconds

    @classmethod
    def from_text(cls, text):
        minutes, seconds = (int(part) for part in text.split(":"))
        return cls(minutes, seconds)

    @staticmethod
    def two_digits(n):
        return f"{n:02d}"

    def __repr__(self):
        return f"Duration({self.minutes}, {self.seconds})"

    def label(self):
        return f"{self.minutes}:{self.two_digits(self.seconds)}"

d = Duration.from_text("3:07")
print(d, d.label())
print(Duration.two_digits(5), d.two_digits(42))
```
```text
Duration(3, 7) 3:07
05 42
```

- `Duration.from_text("3:07")`: Python passes the class as `cls`. The method parses the text and returns `cls(3, 7)`, which runs `__init__` normally.
- `two_digits` needs no duration and no class. It is a plain function that lives in the class because it belongs to the topic. You can call it through the class or through an instance.
- The names `from_...` are common in the standard library: `dict.fromkeys`, `int.from_bytes`.

Class methods also fit work on **class attributes**, because `cls.name = value` changes the class attribute for everyone.

### 6.3 Why `cls(...)` and not the class name

You could write `return Duration(minutes, seconds)`. It works until someone makes a subclass (section 10). Then the hard-coded version returns the **wrong type**:

```python
class Shape:
    def __init__(self, size):
        self.size = size

    @classmethod
    def unit(cls):
        return cls(1)                  # good: respects subclasses

    @staticmethod
    def unit_hardcoded():
        return Shape(1)                # bad: always a Shape

class Square(Shape):
    pass

print(type(Square.unit()).__name__, type(Square.unit_hardcoded()).__name__)
```
```text
Square Shape
```

`Square.unit()` passed `Square` as `cls`, so it built a `Square`. Use `cls`, and alternative constructors keep working for every subclass.

### 6.4 When to use which

- The method reads or changes **this object's data** → instance method.
- It **creates an object** or works with **class-level data** → class method.
- It is a **helper** that uses only its arguments, and belongs near the class → static method. (A plain module-level function is often just as good. Do not force everything into classes.)

### 6.5 Predict the output

```python
class Base:
    kind = "base"

    @classmethod
    def describe(cls):
        return f"{cls.__name__}:{cls.kind}"

    @staticmethod
    def helper(x):
        return x * 2

class Child(Base):
    kind = "child"

c = Child()
print(Base.describe(), Child.describe(), c.describe())
print(Child.helper(4), c.helper(5))
print(Base.describe)
```

<details><summary>Answer</summary>

```text
Base:base Child:child Child:child
8 10
<bound method Base.describe of <class '__main__.Base'>>
```

A class method always receives a **class**: called on `Child` or on an instance of `Child`, `cls` is `Child`, so `cls.kind` is `"child"`. A static method receives exactly what you pass. The last line shows that `Base.describe` is a bound method whose "self" is the class `Base` itself.
</details>

## 7. Encapsulation conventions and name mangling

### 7.1 Encapsulation: hide the details

**Encapsulation** means: a class offers a small, clear set of methods (its **public interface**) and keeps the details of how it works **inside**. Users call `account.deposit(50)`; they do not touch the list where the history is stored. Then you can change the inside later without breaking anyone's code.

Languages like Java enforce this with keywords such as `private`. Python does **not**. It uses **naming conventions** and trusts programmers to respect them.

### 7.2 One underscore: "internal, please do not touch"

A name with **one leading underscore**, such as `self._history`, means: internal detail, may change in the next version, use from outside at your own risk. Python does not stop `account._history`; the underscore is a message to humans, and editors and linters warn about it. You saw the same convention for module names in core.13. Offer a public method (such as `statement()`) for what outsiders really need.

### 7.3 Two underscores: name mangling

A name inside a class that starts with **two underscores** and does **not** end with two underscores, such as `__code`, is **mangled**: Python silently renames it to `_ClassName__code`. This happens when the class body is compiled, for every such name written inside the class.

```python
class Vault:
    def __init__(self):
        self.__code = 1234

    def check(self, guess):
        return guess == self.__code

v = Vault()
print(v.check(1234), vars(v))
print(v._Vault__code)
try:
    print(v.__code)
except AttributeError as e:
    print("AttributeError:", e)
```
```text
True {'_Vault__code': 1234}
1234
AttributeError: 'Vault' object has no attribute '__code'
```

Outside a class body there is no mangling, so `v.__code` looks for a real attribute named `__code`, which does not exist. But `v._Vault__code` works. So mangling is **not security**.

### 7.4 What mangling is really for

Mangling **avoids name clashes in subclasses**. A base class may use `self.__count` for its own purpose, and a subclass written by someone else may also use `self.__count`. Without mangling they would overwrite each other. With mangling they are two attributes:

```python
class Base:
    def __init__(self):
        self.__count = 0            # becomes _Base__count

    def base_tick(self):
        self.__count += 1
        return self.__count

class Child(Base):
    def __init__(self):
        super().__init__()
        self.__count = 100          # becomes _Child__count

    def child_tick(self):
        self.__count += 10
        return self.__count

c = Child()
print(c.base_tick(), c.child_tick(), c.base_tick())
print(vars(c))
```
```text
1 110 2
{'_Base__count': 2, '_Child__count': 110}
```

(`super().__init__()` runs the parent's `__init__`; see section 11.) The exact rules:

- Mangled: names with **at least two leading underscores** and **at most one trailing underscore** (`__x`, `__x_`). Not mangled: `__init__`, `__x__`.
- The class name used is the class where the code is **written**, with its leading underscores removed: inside `class _Helper`, `__x` becomes `_Helper__x`.
- If the class name is only underscores, nothing is mangled.

**Advice:** no underscore for the public interface; **one underscore** for internal details (what you want 95% of the time); two underscores only to avoid clashes in classes that others will subclass, never "for privacy".

### 7.5 Predict the output

```python
class A:
    def __init__(self):
        self.__x = 1
        self._y = 2
        self.__z__ = 3

class B(A):
    def __init__(self):
        super().__init__()
        self.__x = 10

b = B()
print(sorted(vars(b)))
print(b._A__x, b._B__x, b._y, b.__z__)
```

<details><summary>Answer</summary>

```text
['_A__x', '_B__x', '__z__', '_y']
1 10 2 3
```

`__x` is mangled with the name of the class where each line is written: `_A__x` in `A`, `_B__x` in `B`. `_y` has one underscore, so it is untouched. `__z__` ends with two underscores, so it is not mangled.
</details>

## 8. Properties

### 8.1 The problem: public attributes, and then rules arrive

You start with a simple `Product` class whose `price` is a public attribute, and people use `item.price` all over the program. Then a rule arrives: a price can never be negative. In Java style you would hide the attribute behind `get_price()` and `set_price(value)`. But then **every** `item.price` in the program must change.

Python's answer is the **property**. A property looks like an attribute from outside (`item.price`, `item.price = 30`) but runs **methods** behind the scenes. You can start with a plain attribute and switch to a property later, without changing any code that uses the class.

### 8.2 A property with a getter and a setter

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price                # goes through the setter below

    @property
    def price(self):                      # the getter
        return self._price

    @price.setter
    def price(self, value):               # the setter
        if value < 0:
            raise ValueError(f"price cannot be negative: {value}")
        self._price = value

item = Product("tea", 120)
item.price = 150
print(item.price, vars(item))
for bad in [lambda: setattr(item, "price", -5), lambda: Product("milk", -1)]:
    try:
        bad()
    except ValueError as e:
        print("refused:", e)
```
```text
150 {'name': 'tea', '_price': 150}
refused: price cannot be negative: -5
refused: price cannot be negative: -1
```

Step by step:

- `@property` turns the first `price` method into a **property** object stored on the class. Reading `item.price` calls this getter.
- `@price.setter` adds a setter to **the same** property; both methods must have the same name. `item.price = 150` calls the setter with `value = 150`. (`setattr(item, "price", -5)` does the same as `item.price = -5`; we use it only to fit the test in a `lambda`.)
- The real value lives in a **backing attribute** with a different name, `_price`. If the setter did `self.price = value`, it would call itself forever (`RecursionError`).
- In `__init__`, `self.price = price` already goes through the setter, so construction is checked too. Validate in **one** place: the setter.

### 8.3 Computed and read-only properties

A property does not have to store anything. It can **compute** a value from other attributes, so it is always up to date. A property **without a setter** is read-only:

```python
class Square:
    def __init__(self, side):
        self.side = side

    @property
    def area(self):
        return self.side ** 2

    @property
    def perimeter(self):
        return 4 * self.side

    @perimeter.setter
    def perimeter(self, value):
        self.side = value / 4

sq = Square(3)
print(sq.area, sq.perimeter)
sq.perimeter = 20
print(sq.side, sq.area)
sq.area = 10
```
```text
9 12
5.0 25.0
Traceback (most recent call last):
  ...
AttributeError: property 'area' of 'Square' object has no setter
```

Only `side` is stored. `area` and `perimeter` are computed from it, so they can never disagree. `perimeter` can be set (the setter converts back to `side`); `area` has no setter, so assigning to it is refused with a clear message.

A property can also have a **deleter** (`@area.deleter`), which runs on `del obj.area`. It is rarely needed; one use is clearing a cached value.

### 8.4 When to use a property

- Use a **plain attribute** first. A property that only returns `self._x` and sets `self._x` with no rule is extra code for nothing, and you can switch later without breaking users.
- Use a property for **validation**, a **computed** value, or a **read-only** view.
- A property must be **cheap** and have **no surprising side effects**. If reading it does real work (a long computation, a file, the network), make it a method: `obj.compute_total()`.

### 8.5 Predict the output

```python
class Wallet:
    def __init__(self, amount):
        self.amount = amount

    @property
    def amount(self):
        print("get")
        return self._amount

    @amount.setter
    def amount(self, value):
        print("set", value)
        self._amount = max(0, value)

w = Wallet(-5)
w.amount += 10
print(w.amount)
```

<details><summary>Answer</summary>

```text
set -5
get
set 10
get
10
```

`Wallet(-5)` calls the setter, which stores `max(0, -5) = 0`. `w.amount += 10` is `w.amount = w.amount + 10`: first a **get** (0), then a **set** with 10. `print(w.amount)` does one more **get**.
</details>

## 9. How attribute lookup really works

### 9.1 The full order

You now know instance attributes, class attributes (including methods) and properties. When you read `obj.name`, Python decides like this:

1. Look for `name` on the **class** and its parents (in **MRO** order, section 12). If it is found and it is a **data descriptor** (an object that controls reading and writing, such as a **property**), use it. It wins.
2. Otherwise, look in the **instance `__dict__`**. If found, return that value.
3. Otherwise, if step 1 found something: return a **bound method** if it is a function, or the value itself otherwise.
4. Otherwise, raise **`AttributeError`**.

You need the word "descriptor" only here. Remember: **a property beats the instance dictionary; the instance dictionary beats everything else on the class.** For **assignment**, `obj.name = value`: if the class has a property `name`, its setter runs (or `AttributeError` if there is none); otherwise the value goes into the instance `__dict__`.

### 9.2 Seeing the order in action

```python
class Demo:
    kind = "class attribute"

    def greet(self):
        return "method from class"

    @property
    def size(self):
        return "property"

d = Demo()
d.__dict__["kind"] = "instance value"
d.__dict__["greet"] = lambda: "function in instance"
d.__dict__["size"] = "instance size"
print(d.kind)
print(d.greet())
print(d.size)
```
```text
instance value
function in instance
property
```

We wrote straight into `__dict__`, because normal assignment to `d.size` would call the property. Then: the instance value hides the class attribute `kind`; the instance function hides the method (and is called with **no** argument, because it is not bound); but the **property wins** over the instance value `"instance size"`.

### 9.3 Tools to look at objects

| Tool | What it gives |
|---|---|
| `vars(obj)` / `obj.__dict__` | the instance's own attributes |
| `vars(Cls)` | what is defined directly in the class body |
| `dir(obj)` | all names reachable from `obj`, sorted |
| `hasattr(obj, "name")` | `True` if reading would succeed |
| `getattr(obj, "name", default)` | read by a name in a string, with an optional default |
| `setattr(obj, "name", value)` | assign by a name in a string |

`getattr` and `setattr` help when the attribute name comes from data, for example a key from a settings file:

```python
class Settings:
    def __init__(self):
        self.theme = "light"
        self.font_size = 12

s = Settings()
for key, value in [("theme", "dark"), ("font_size", 14)]:
    setattr(s, key, value)
print(vars(s))
print(getattr(s, "theme"), getattr(s, "colour", "not set"), hasattr(s, "volume"))
print(s.font_sise)
```
```text
{'theme': 'dark', 'font_size': 14}
dark not set False
Traceback (most recent call last):
  ...
AttributeError: 'Settings' object has no attribute 'font_sise'. Did you mean: 'font_size'?
```

The `AttributeError` names the **type** and the missing name, and Python 3.14 adds "Did you mean" when there is a close match. When you see "has no attribute", check for a typo, an attribute set only in some methods (not in `__init__`), or a forgotten `self.`.


## 10. Inheritance and overriding

### 10.1 The "is-a" relationship

Often one kind of thing is a **special case** of another. An intern **is an** employee. A savings account **is an** account. A `FileNotFoundError` **is an** `OSError`. **Inheritance** lets you write a new class (the **subclass**, or child) that starts with everything from an existing class (the **base class**, or parent), and then adds or changes some parts.

```python
class Employee:
    def __init__(self, name):
        self.name = name

    def monthly_pay(self):
        return 30000

    def payslip(self):
        return f"{self.name}: {self.monthly_pay()} INR"

class Intern(Employee):
    def monthly_pay(self):
        return 12000

class Contractor(Employee):
    def monthly_pay(self):
        return 45000

    def invoice(self):
        return f"invoice from {self.name}"

for person in [Employee("Asha"), Intern("Ravi"), Contractor("Mira")]:
    print(person.payslip())
print(Contractor("Mira").invoice())
```
```text
Asha: 30000 INR
Ravi: 12000 INR
Mira: 45000 INR
invoice from Mira
```

- `class Intern(Employee):` means "`Intern` inherits from `Employee`". `Intern` gets `__init__`, `monthly_pay` and `payslip` for free.
- `Intern` **overrides** `monthly_pay`: it defines a method with the same name, which replaces the parent's version for interns.
- `Contractor` also **extends** the parent with a new method, `invoice`.

### 10.2 How the lookup finds inherited methods

There is no copying. When you call `ravi.payslip()` on an intern, the lookup rule from section 5.1 searches the instance, then `Intern`, then **`Employee`**, and finds `payslip` there. Every class that does not name a parent inherits from **`object`**, the root of all classes. That is where default methods such as `__repr__` and `__init__` come from.

You can see the parent in `Intern.__bases__`, which is the tuple `(Employee,)`. And `"payslip" in vars(Intern)` is `False`: the method lives only in `Employee`.

### 10.3 The template method pattern: the parent calls `self.hook()`

Look again at `payslip`. It is written once, in `Employee`, and it calls `self.monthly_pay()`. When `payslip` runs for an `Intern`, `self` is the intern, so `self.monthly_pay()` finds `Intern.monthly_pay`. **The parent's code calls the child's method.** This is one of the most useful ideas in OOP: the base class fixes the **steps** of an algorithm, and subclasses fill in the **details**.

```python
class Report:
    def render(self):
        lines = [self.header()]
        for row in self.rows():
            lines.append(self.format_row(row))
        return "\n".join(lines)

    def header(self):
        return "REPORT"

    def format_row(self, row):
        return str(row)

class SalesReport(Report):
    def __init__(self, sales):
        self.sales = sales

    def header(self):
        return "Sales (INR)"

    def rows(self):
        return sorted(self.sales.items())

    def format_row(self, row):
        item, amount = row
        return f"  {item:<8}{amount:>6}"

print(SalesReport({"tea": 120, "coffee": 340}).render())
```
```text
Sales (INR)
  coffee     340
  tea        120
```

`render` never changes. `SalesReport` supplies `rows` and changes `header` and `format_row`. (Notice that `Report` itself has no `rows` method. A plain `Report().render()` would fail. Section 16 shows how to say "subclasses **must** provide this" properly.)

### 10.4 `isinstance` and `issubclass`

`isinstance(obj, Cls)` is `True` if `obj` is an instance of `Cls` **or of any subclass**. `issubclass(A, B)` asks the same question about classes. Both accept a tuple of classes.

```python
ravi = Intern("Ravi")
print(isinstance(ravi, Intern), isinstance(ravi, Employee), isinstance(ravi, Contractor))
print(issubclass(Intern, Employee), issubclass(Employee, Intern))
print(isinstance(ravi, (Contractor, Intern)))
print(type(ravi) == Employee)
```
```text
True True False
True False
True
False
```

The last line shows the difference between `type(...) ==` and `isinstance`: `type` gives the exact class only, so it ignores inheritance. Prefer `isinstance`.

When you check several classes in a row, test the **most specific class first**. Every `Intern` is also an `Employee`, so an `isinstance(p, Employee)` test placed first would also catch the interns, and the `Intern` branch would never run. You will meet the same rule with `except` clauses in section 17, and section 15 explains why you often need no `isinstance` at all.

### 10.5 Predict the output

```python
class Vehicle:
    wheels = 4

    def info(self):
        return f"{type(self).__name__}: {self.wheels} wheels, {self.fuel()}"

    def fuel(self):
        return "petrol"

class Bike(Vehicle):
    wheels = 2

class ECar(Vehicle):
    def fuel(self):
        return "electric"

class EBike(Bike):
    def fuel(self):
        return "battery"

for v in [Vehicle(), Bike(), ECar(), EBike()]:
    print(v.info())
```

<details><summary>Answer</summary>

```text
Vehicle: 4 wheels, petrol
Bike: 2 wheels, petrol
ECar: 4 wheels, electric
EBike: 2 wheels, battery
```

`info` is written once. For each object, `self.wheels` and `self.fuel()` are looked up starting at the object's **own** class. `EBike` gets `wheels = 2` from `Bike` and its own `fuel`.
</details>

## 11. `super()` in single inheritance

### 11.1 Extending a method instead of replacing it

When a subclass overrides a method, the parent's version is hidden. Often you do not want to **replace** the parent's work but to **add** to it. `super()` gives you access to the parent's version:

```python
class Course:
    def __init__(self, code, credits):
        if credits <= 0:
            raise ValueError("credits must be positive")
        self.code = code
        self.credits = credits

    def fee(self):
        return self.credits * 1000

class LabCourse(Course):
    def __init__(self, code, credits, lab_fee):
        super().__init__(code, credits)       # let Course set (and check) its part
        self.lab_fee = lab_fee                # then add ours

    def fee(self):
        return super().fee() + self.lab_fee   # reuse the parent's rule, add to it

lab = LabCourse("BCA-204", 4, 1500)
print(vars(lab))
print(lab.fee(), Course("BCA-101", 3).fee())
```
```text
{'code': 'BCA-204', 'credits': 4, 'lab_fee': 1500}
5500 3000
```

- `super().__init__(code, credits)` runs `Course.__init__` **on the same object**, so `code` and `credits` are checked and set exactly as the parent wants. Then the child adds `lab_fee`.
- `LabCourse.fee` reuses the parent's calculation and adds the lab fee. If the parent's fee rule changes, the lab course follows automatically.

You could write `Course.__init__(self, code, credits)` instead, and in single inheritance it does the same. But `super()` does not repeat the parent's name, and it works correctly with multiple inheritance (section 12). Always prefer `super()`.

### 11.2 Forgetting to call the parent's `__init__`

If a subclass defines `__init__` and does **not** call `super().__init__(...)`, the parent's `__init__` never runs, and its attributes are never set:

```python
class Device:
    def __init__(self, name):
        self.name = name

class Printer(Device):
    def __init__(self, name, pages_per_minute):
        self.ppm = pages_per_minute          # forgot super().__init__(name)

    def label(self):
        return f"{self.name} ({self.ppm} ppm)"

print(Printer("HP-1", 20).label())
```
```text
Traceback (most recent call last):
  ...
AttributeError: 'Printer' object has no attribute 'name'
```

The error appears far away from the real mistake. If your subclass has `__init__`, its first line is almost always `super().__init__(...)`. (If the subclass does not define `__init__` at all, the parent's is inherited and runs automatically.)

### 11.3 A chain of `__init__` methods

Each level handles only its own attributes and passes the rest up:

```python
class Vehicle:
    def __init__(self, brand):
        print("Vehicle.__init__")
        self.brand = brand

class Car(Vehicle):
    def __init__(self, brand, seats):
        print("Car.__init__ start")
        super().__init__(brand)
        self.seats = seats
        print("Car.__init__ end")

class ElectricCar(Car):
    def __init__(self, brand, seats, battery_kwh):
        print("ElectricCar.__init__ start")
        super().__init__(brand, seats)
        self.battery_kwh = battery_kwh
        print("ElectricCar.__init__ end")

e = ElectricCar("Tata", 5, 40)
print(vars(e))
```
```text
ElectricCar.__init__ start
Car.__init__ start
Vehicle.__init__
Car.__init__ end
ElectricCar.__init__ end
{'brand': 'Tata', 'seats': 5, 'battery_kwh': 40}
```

Read the order. Each `__init__` starts, then hands over to its parent with `super()`, until `Vehicle` runs. Then the rest of each `__init__` finishes, in the opposite order. Code **before** `super()` runs child first; code **after** it runs parent first.

## 12. Multiple inheritance and the MRO

### 12.1 A class with two parents

A class may inherit from **several** classes. List them all in the brackets:

```python
class Flyer:
    def move(self):
        return "fly"

    def land(self):
        return "land on a branch"

class Swimmer:
    def move(self):
        return "swim"

    def dive(self):
        return "dive"

class Duck(Flyer, Swimmer):
    pass

d = Duck()
print(d.move(), "|", d.land(), "|", d.dive())
print([c.__name__ for c in Duck.__mro__])
```
```text
fly | land on a branch | dive
['Duck', 'Flyer', 'Swimmer', 'object']
```

`Duck` gets `land` from `Flyer` and `dive` from `Swimmer`. Both define `move`: which one wins? Python searches the classes in a fixed order, the **method resolution order** (**MRO**), shown by `Duck.__mro__` (a tuple) or `Duck.mro()` (a list). Here it is `Duck, Flyer, Swimmer, object`, so `Flyer.move` wins. The order of the bases matters: `class Duck(Swimmer, Flyer)` would swim. **Every attribute lookup follows the MRO.** With one parent it is simply the chain up to `object`; with several parents it needs a rule.

### 12.2 The diamond

The interesting case is the **diamond**: two classes inherit from the same base, and a fourth class inherits from both.

```text
        A
       / \
      B   C
       \ /
        D
```

```python
class A:
    def who(self):
        return "A"

class B(A):
    def who(self):
        return "B"

class C(A):
    def who(self):
        return "C"

class D(B, C):
    pass

print([k.__name__ for k in D.__mro__])
print(D().who())
```
```text
['D', 'B', 'C', 'A', 'object']
B
```

The MRO is `D, B, C, A, object`. Notice that `A` comes **after both** `B` and `C`, even though `B` is a direct child of `A`. A simple "depth-first" search (D, B, A, C, A) would visit `A` before `C`, and then `A.who` could hide `C.who`, which is wrong: `C` is more specific than `A`. Python uses an algorithm called **C3 linearization** to build an order that respects two promises:

1. **A child always comes before its parents.** (`B` and `C` before `A`; `D` before everything.)
2. **The order of the bases in each class statement is kept.** (`class D(B, C)` puts `B` before `C`.)

And it keeps the orders of the parents' own MROs. If no order can keep all these promises, Python refuses to create the class.

### 12.3 C3 by hand: the rule

Write `L[X]` for the MRO (the "linearization") of class `X`, as a list. For `object`, `L[object] = [object]`. For a class `X` with bases `B1, B2, ..., Bn`:

```text
L[X] = [X] + merge(L[B1], L[B2], ..., L[Bn], [B1, B2, ..., Bn])
```

So you merge the MROs of all parents **plus** the list of the parents themselves. The **merge** works like this:

1. Look at the **first** element (the **head**) of the first list.
2. It is a **good head** if it does **not** appear in the **tail** (any position except the first) of **any** list.
3. If it is good: append it to the result and **remove it from every list** where it appears. Go back to step 1, starting again with the first non-empty list.
4. If it is not good: try the head of the **next** list, and so on.
5. When all lists are empty, you are done. If no list has a good head, the merge **fails** (section 12.6).

The "not in any tail" test is what guarantees promise 1: a class that still has some child waiting in front of it (in some list) cannot go next.

### 12.4 C3 by hand: the diamond

Start from the top and go down. `O` means `object`.

```text
L[A] = [A, O]
L[B] = [B] + merge([A, O], [A])  = [B, A, O]
L[C] = [C] + merge([A, O], [A])  = [C, A, O]
```

Now `D(B, C)`:

```text
L[D] = [D] + merge([B, A, O], [C, A, O], [B, C])
```

Work step by step. At each step, write the lists, pick a head, check the tails.

| Step | Lists | Candidate | In some tail? | Result so far |
|---|---|---|---|---|
| 1 | `[B,A,O] [C,A,O] [B,C]` | `B` | tails are `[A,O] [A,O] [C]`: no | `D B` |
| 2 | `[A,O] [C,A,O] [C]` | `A` | yes, in `[C,A,O]` | |
| 2 | | `C` (next list) | tails `[O] [A,O] []`: no | `D B C` |
| 3 | `[A,O] [A,O]` | `A` | tails `[O] [O]`: no | `D B C A` |
| 4 | `[O] [O]` | `O` | no | `D B C A O` |

At step 2, `A` was refused because `C` (a child of `A`) was still waiting in front of it. So `C` went first. The result `D, B, C, A, object` matches what Python printed.

### 12.5 C3 by hand: a bigger example

```text
level 0:            object
level 1:        D      E      F
level 2:     B(D, E)      C(D, F)
level 3:          A(B, C)
```

The classes are: `D`, `E`, `F` each inherit from `object`; `B(D, E)`; `C(D, F)`; `A(B, C)`. First, the small ones:

```text
L[D] = [D, O]      L[E] = [E, O]      L[F] = [F, O]
L[B] = [B] + merge([D,O], [E,O], [D,E]) = [B, D, E, O]
L[C] = [C] + merge([D,O], [F,O], [D,F]) = [C, D, F, O]
```

Check `L[B]` yourself: `D` is good (tails `[O] [O] [E]`), then `E`? The lists are `[O] [E,O] [E]`; the head `O` is in the tail of `[E,O]`, so try `E`: good. Then `O`.

Now the big merge:

```text
L[A] = [A] + merge([B,D,E,O], [C,D,F,O], [B,C])
```

| Step | Lists | Candidate | Good? | Result so far |
|---|---|---|---|---|
| 1 | `[B,D,E,O] [C,D,F,O] [B,C]` | `B` | yes | `A B` |
| 2 | `[D,E,O] [C,D,F,O] [C]` | `D` | no: in tail of `[C,D,F,O]` | |
| 2 | | `C` | yes | `A B C` |
| 3 | `[D,E,O] [D,F,O]` | `D` | yes | `A B C D` |
| 4 | `[E,O] [F,O]` | `E` | yes | `A B C D E` |
| 5 | `[O] [F,O]` | `O` | no: in tail of `[F,O]` | |
| 5 | | `F` | yes | `A B C D E F` |
| 6 | `[O] [O]` | `O` | yes | `A B C D E F O` |

Let Python check our paper work:

```python
class D: pass
class E: pass
class F: pass
class B(D, E): pass
class C(D, F): pass
class A(B, C): pass

print([k.__name__ for k in A.__mro__])
print([k.__name__ for k in B.mro()])
print([k.__name__ for k in C.mro()])
```
```text
['A', 'B', 'C', 'D', 'E', 'F', 'object']
['B', 'D', 'E', 'object']
['C', 'D', 'F', 'object']
```

A useful shortcut for checking: in the final MRO, every class appears before all of its parents, and for every class statement the bases appear in the written order.

### 12.6 When there is no valid order

Sometimes the promises contradict each other. Then `class` raises `TypeError`:

```python
class Base: pass
class Child(Base): pass

class Broken(Base, Child):
    pass
```
```text
Traceback (most recent call last):
  ...
TypeError: Cannot create a consistent method resolution order (MRO) for bases Base, Child
```

Do the merge: `L[Broken] = [Broken] + merge([Base, O], [Child, Base, O], [Base, Child])`. The head `Base` is in the tail of `[Child, Base, O]` (a child must come first). The next head, `Child`, is in the tail of `[Base, Child]` (the class statement says `Base` first). The last head, `Base` again, is refused. No good head: the merge fails. The fix is to list the more specific class first: `class Fixed(Child, Base)`, or simply `class Fixed(Child)`.

### 12.7 `super()` follows the MRO, not the parent

Here is the most important fact about `super()`: it does **not** mean "my parent". `super()` means "**the next class after mine in the MRO of the object's class**". In single inheritance those are the same. In a diamond they are not:

```python
class A:
    def hello(self):
        print("A.hello")

class B(A):
    def hello(self):
        print("B.hello")
        super().hello()

class C(A):
    def hello(self):
        print("C.hello")
        super().hello()

class D(B, C):
    def hello(self):
        print("D.hello")
        super().hello()

D().hello()
print("---")
B().hello()
```
```text
D.hello
B.hello
C.hello
A.hello
---
B.hello
A.hello
```

For a `D` object the MRO is `D, B, C, A`. So `super()` inside `B.hello` called **`C.hello`**, a class that `B` does not even know about! For a plain `B` object, the MRO is `B, A`, and the same line in `B` calls `A.hello`. And `A.hello` runs **exactly once**, even though two classes inherit from it. This is called **cooperative** multiple inheritance: each class does its part and passes control along the MRO.

### 12.8 Cooperative `__init__` with `**kwargs`

The difficult part is `__init__`. Different classes in the MRO need different arguments, and a class does not know which class comes next. The solution is the **keyword-arguments pattern**:

- every `__init__` takes the arguments it needs **by keyword**, plus `**kwargs` for the rest;
- it passes `**kwargs` on with `super().__init__(**kwargs)`;
- by the time the chain reaches `object.__init__`, every keyword has been used.

```python
class Named:
    def __init__(self, *, name, **kwargs):
        print("Named")
        super().__init__(**kwargs)
        self.name = name

class Priced:
    def __init__(self, *, price, **kwargs):
        print("Priced")
        super().__init__(**kwargs)
        self.price = price

class Product(Named, Priced):
    def __init__(self, *, sku, **kwargs):
        print("Product")
        super().__init__(**kwargs)
        self.sku = sku

p = Product(sku="T-01", name="Tea", price=120)
print(vars(p))
print([k.__name__ for k in Product.__mro__])
```
```text
Product
Named
Priced
{'price': 120, 'name': 'Tea', 'sku': 'T-01'}
['Product', 'Named', 'Priced', 'object']
```

Each class took **its** keyword out of `kwargs` and passed the rest on. (The `*` in the parameter list makes the following parameters keyword-only, which you met in core.06.) `Named.__init__` called `super().__init__(**kwargs)`, which went to `Priced`, not to `object`. If a keyword is left over or misspelled, it reaches `object.__init__`, which accepts no extra arguments:

```python
Product(sku="T-02", name="Coffee", price=90, colour="brown")
```
```text
Product
Named
Priced
Traceback (most recent call last):
  ...
TypeError: object.__init__() takes exactly one argument (the instance to initialize)
```

The message is a little cryptic. It means: `object.__init__` received more than the instance (here the leftover `colour="brown"`). Still, the error is useful: no argument is silently ignored.

Compare with the old way, calling parents **by name**. If `Left.__init__` and `Right.__init__` each call `Base.__init__(self)`, and `Both.__init__` calls `Left.__init__(self)` and then `Right.__init__(self)`, then `Base.__init__` runs **twice**. If it opened a file or added the object to a list, that would happen twice. With `super().__init__()` everywhere, each `__init__` in the MRO runs exactly once.

### 12.9 Predict the output

```python
class Root:
    def tag(self):
        return ["Root"]

class X(Root):
    def tag(self):
        return ["X"] + super().tag()

class Y(Root):
    def tag(self):
        return ["Y"] + super().tag()

class Z(Root):
    def tag(self):
        return ["Z"] + super().tag()

class P(X, Y):
    def tag(self):
        return ["P"] + super().tag()

class Q(P, Z):
    pass

print(Q().tag())
print(P().tag())
```

First compute `L[Q]` on paper.

<details><summary>Answer</summary>

```text
['P', 'X', 'Y', 'Z', 'Root']
['P', 'X', 'Y', 'Root']
```

`L[P] = [P] + merge([X,Root,O], [Y,Root,O], [X,Y]) = [P, X, Y, Root, O]`. `Q` has no `tag` of its own, so the lookup starts with `P.tag`. Then `L[Q] = [Q] + merge([P,X,Y,Root,O], [Z,Root,O], [P,Z])`: take `P`, `X`, `Y` (all good); `Root` is in the tail of `[Z,Root,O]`, so take `Z`; then `Root`, `O`. So `L[Q] = Q, P, X, Y, Z, Root, object`, and each `super().tag()` moves one step along it. For a plain `P`, `Z` is not in the MRO at all.
</details>

**Advice.** Use multiple inheritance mainly for **mixins** (next section). If several classes in a hierarchy override the same method, **all of them** should call `super()`, and their `__init__` methods should accept `**kwargs`. When in doubt, print `Cls.__mro__`; do not guess.

## 13. Mixins

### 13.1 What a mixin is

A **mixin** is a small class that adds **one behaviour** to other classes through multiple inheritance. It is not meant to be used alone, and it usually has **no `__init__`** and no data of its own. It only has methods that rely on things the main class already provides.

```python
class ReprMixin:
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({fields})"

class Book(ReprMixin):
    def __init__(self, title, year):
        self.title = title
        self.year = year

class Member(ReprMixin):
    def __init__(self, name):
        self.name = name

print([Book("Godan", 1936), Member("Asha")])
```
```text
[Book(title='Godan', year=1936), Member(name='Asha')]
```

`Book` and `Member` are unrelated classes, but both gain a useful `__repr__` without copying code. `ReprMixin` does not care what the object is; it only uses `type(self)` and `vars(self)`.

### 13.2 Rules for mixins

- **Name them** with the suffix `Mixin`: `ReprMixin`, `JsonMixin`, `LoggingMixin`. Then a reader knows the class is not a full type.
- **Put mixins first** (to the left) in the bases, and the main base class **last**: `class Book(JsonMixin, ReprMixin, Item)`. Then mixin methods come earlier in the MRO and can extend the base's methods with `super()`.
- **Keep them small**: one behaviour, few methods, no `__init__` if possible. If a mixin must keep state, create it lazily the first time it is needed (`if not hasattr(self, "_log"): self._log = []`), or use the `**kwargs` pattern from 12.8.
- A mixin that overrides a method of the main class **must call `super()`**, so the real method still runs.

### 13.3 A mixin that extends a method

```python
class Counter:
    def __init__(self):
        self.value = 0

    def add(self, n):
        self.value += n

class NonNegativeMixin:
    def add(self, n):
        if n < 0:
            raise ValueError(f"negative step: {n}")
        super().add(n)                     # the real work, in Counter

class SafeCounter(NonNegativeMixin, Counter):
    pass

c = SafeCounter()
c.add(5)
try:
    c.add(-2)
except ValueError as e:
    print("refused:", e)
print(c.value, [k.__name__ for k in SafeCounter.__mro__])
```
```text
refused: negative step: -2
5 ['SafeCounter', 'NonNegativeMixin', 'Counter', 'object']
```

`NonNegativeMixin.add` comes first in the MRO. It checks the argument and then passes on to `Counter.add` with `super()`. Swap the bases (`class SafeCounter(Counter, NonNegativeMixin)`) and `Counter.add` would be found first: the check would never run. Mixin order matters. The same mixin could guard any class that has an `add(n)` method.


## 14. Composition vs inheritance

### 14.1 "Has-a" instead of "is-a"

Inheritance says "an intern **is an** employee". **Composition** says "a phone **has a** battery": one object keeps another object in an attribute and uses it. The outer object **delegates** work to the inner one.

```python
class Battery:
    def __init__(self, capacity):
        self.capacity = capacity
        self.charge = capacity

    def use(self, amount):
        if amount > self.charge:
            raise RuntimeError("battery empty")
        self.charge -= amount

class Phone:
    def __init__(self, model):
        self.model = model
        self.battery = Battery(100)          # the phone HAS a battery

    def call(self, minutes):
        self.battery.use(minutes * 2)        # delegate
        return f"{self.model}: {self.battery.charge}% left"

phone = Phone("Nokia")
print(phone.call(10))
print(phone.call(30))
```
```text
Nokia: 80% left
Nokia: 20% left
```

A phone is not a kind of battery, so `class Phone(Battery)` would be wrong, even though it would "work". The test is simple: say the sentence aloud. "A phone **is a** battery" is false. "A phone **has a** battery" is true. Use composition.

### 14.2 The `Stack(list)` leak

Inheritance gives the child **everything** from the parent, including things you did not want. Suppose you want a stack: only `push`, `pop` and `peek`. It is tempting to inherit from `list`:

```python
class Stack(list):
    def push(self, item):
        self.append(item)

    def peek(self):
        return self[-1]

s = Stack()
s.push(1)
s.push(2)
s.insert(0, 99)      # not a stack operation, but it works
s.sort(reverse=True)
print(s, s.peek())
```
```text
[99, 2, 1] 1
```

`peek` returns `1`, but the last item pushed was `2`: the stack is broken. `Stack` **is a** list, so it has `insert`, `sort`, `remove`, indexing, slicing and about 40 other methods. Anyone can break the "last in, first out" rule, and you can never change the inside (say, to a linked list) without breaking users who called `insert`. With composition, the class decides exactly what is public:

```python
class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

s = Stack()
s.push(1)
s.push(2)
print(s.pop(), hasattr(s, "insert"))
```
```text
2 False
```

### 14.3 Strategy objects: change behaviour at run time

Composition also lets you **swap** a part while the program runs. An object's class is fixed when it is made, but an attribute can hold a different helper object at any time:

```python
class StandardShipping:
    def cost(self, total):
        return 50

class FreeAbove:
    def __init__(self, limit):
        self.limit = limit

    def cost(self, total):
        return 0 if total >= self.limit else 80

class Order:
    def __init__(self, total, shipping):
        self.total = total
        self.shipping = shipping             # the strategy

    def amount_due(self):
        return self.total + self.shipping.cost(self.total)

order = Order(600, StandardShipping())
print(order.amount_due())
order.shipping = FreeAbove(500)
print(order.amount_due(), Order(300, FreeAbove(500)).amount_due())
```
```text
650
600 380
```

With inheritance you would need `StandardOrder`, `FreeAboveOrder`, and so on; add three kinds of payment and you need nine classes. With composition you write each part once and combine them freely. This is why many designers say: **prefer composition over inheritance**.

### 14.4 How to choose

| Use inheritance when... | Use composition when... |
|---|---|
| "X **is a** Y" is true in every situation | "X **has a** Y" or "X **uses a** Y" is true |
| X should work **everywhere** a Y is expected | X needs only **some** of Y's abilities |
| X keeps all of Y's rules | you want to hide Y's other methods |
| the relationship never changes | the part may be **swapped** at run time |

A useful check for inheritance: could code written for the parent receive the child without surprises? A `LabCourse` can go anywhere a `Course` goes. A `Stack(list)` given to code that calls `insert(0, x)` silently breaks the stack's rules. When in doubt, choose composition; it is easier to change later.

## 15. Polymorphism and duck typing

### 15.1 One call, many behaviours

**Polymorphism** ("many shapes") means: the same call does the right thing for different kinds of objects. You saw it in section 10: `person.payslip()` worked for employees, interns and contractors, each with its own `monthly_pay`. The code that uses the objects needs no `if` statements about their types. A function that adds up `s.area()` for a list of shapes works for circles and squares alike, and it keeps working when someone adds a `Triangle` class next year.

### 15.2 Duck typing

"If it walks like a duck and quacks like a duck, then it is a duck." In Python, what matters is **what an object can do**, not **what class it is**. This is **duck typing**, and you have used it all along: a `for` loop works on lists, strings, files and generators, because all of them can be iterated. The objects do not even need a common base class.

```python
import io

class Shouter:
    def __init__(self):
        self.parts = []

    def write(self, text):
        self.parts.append(text.upper())

def save_log(lines, out):
    for line in lines:
        out.write(line + "\n")

buffer = io.StringIO()
save_log(["start", "stop"], buffer)
loud = Shouter()
save_log(["start", "stop"], loud)
print(repr(buffer.getvalue()), loud.parts)
```
```text
'start\nstop\n' ['START\n', 'STOP\n']
```

`save_log` never checks a type. It works with a real file, an `io.StringIO` (core.12), or our own `Shouter`, because each has a `write` method. This also makes testing easy: a test can pass a simple fake object instead of a real file.

### 15.3 EAFP vs LBYL

When you are not sure an object can do something, there are two styles:

- **LBYL**, "look before you leap": check first. `if hasattr(obj, "close"): obj.close()`.
- **EAFP**, "easier to ask forgiveness than permission": just try, and handle the failure.

```python
class Connection:
    def close(self):
        return "connection closed"

class TempFile:
    def close(self):
        return "temp file closed"

def close_all(things):
    messages = []
    for thing in things:
        try:
            close = thing.close              # only the lookup is inside try
        except AttributeError:
            continue                         # cannot be closed: skip it
        messages.append(close())
    return messages

print(close_all([Connection(), 42, TempFile(), "text"]))
```
```text
['connection closed', 'temp file closed']
```

Python usually prefers **EAFP**. It is often shorter, and it avoids a gap between the check and the action (in core.12 a file could disappear between `exists()` and `open()`). Notice the detail: the `try` covers only the **lookup** `thing.close`, not the call `close()`. Otherwise an `AttributeError` raised by a bug **inside** `close` would be silently hidden. Keep `try` blocks small.

### 15.4 When `isinstance` is right

Duck typing does not mean "never use `isinstance`". It is right when you must treat **different kinds of input differently** (one string or a list of strings?), when you check an **ability** with an abstract base class (next section), or when you **validate input** at the edge of your program to give a clear error. What to avoid is checking one **concrete** class when any object with the right methods would do: `if type(out) == io.StringIO` would reject a real file and our `Shouter`.

### 15.5 Predict the output

```python
class Cat:
    def speak(self):
        return "meow"

class Broken:
    def speak(self):
        return self.sound          # bug: no such attribute

def noises(things):
    out = []
    for t in things:
        try:
            out.append(t.speak())
        except AttributeError:
            out.append("?")
    return out

print(noises([Cat(), 42, Broken()]))
```

<details><summary>Answer</summary>

```text
['meow', '?', '?']
```

`42` has no `speak`, so `"?"` is right. But `Broken` **has** `speak`; the `AttributeError` comes from a bug inside it, and the wide `try` hid that bug as `"?"`. Narrowing the `try` to the lookup (as in 15.3) would let the real bug show.
</details>

## 16. Abstract base classes

### 16.1 The problem: "subclasses must provide this"

In section 10.3, `Report.render` called `self.rows()`, but `Report` had no `rows`. Nothing forced a subclass to write it; the error came only when `render` ran. An **abstract base class** (ABC) states the rule clearly: "every concrete subclass **must** implement these methods". Python checks it when you try to create an object.

```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def connect(self):
        """Prepare the channel."""

    @abstractmethod
    def send(self, to, text):
        """Send one message and return a short receipt."""

    def broadcast(self, people, text):        # a normal (concrete) method
        self.connect()
        return [self.send(p, text) for p in people]

class SmsNotifier(Notifier):
    def connect(self):
        pass

    def send(self, to, text):
        return f"SMS to {to}: {text[:10]}"

print(SmsNotifier().broadcast(["Asha", "Ravi"], "Library closes at 6 today"))
print(Notifier.__abstractmethods__)
print(SmsNotifier.__abstractmethods__)
```
```text
['SMS to Asha: Library cl', 'SMS to Ravi: Library cl']
frozenset({'send', 'connect'})
frozenset()
```

- `class Notifier(ABC)` makes `Notifier` an abstract base class.
- `@abstractmethod` marks methods that subclasses must override. The body can be just a docstring.
- Python records the names of the methods that are still abstract in the class attribute **`__abstractmethods__`**, a `frozenset` (an unchangeable set; the order in which it prints may differ). For `SmsNotifier` it is empty: everything is implemented.
- `broadcast` is a normal method that subclasses inherit. An ABC mixes rules ("you must have `send`") with shared code ("here is `broadcast` for free").

### 16.2 Instantiation is refused

A class whose `__abstractmethods__` is not empty cannot be instantiated. The check happens when you **create** an object, not when you define the class:

```python
class PushNotifier(Notifier):
    def send(self, to, text):
        return "push"

print("class created", PushNotifier.__abstractmethods__)
for cls in [Notifier, PushNotifier]:
    try:
        cls()
    except TypeError as e:
        print("TypeError:", e)
```
```text
class created frozenset({'connect'})
TypeError: Can't instantiate abstract class Notifier without an implementation for abstract methods 'connect', 'send'
TypeError: Can't instantiate abstract class PushNotifier without an implementation for abstract method 'connect'
```

This is much better than finding out later, deep inside some call to `broadcast`. The message names exactly what is missing.

### 16.3 Abstract properties

You can combine `@property` with `@abstractmethod`. Put `@property` on the outside:

```python
from abc import ABC, abstractmethod

class Plugin(ABC):
    @property
    @abstractmethod
    def name(self):
        """A short name for the plugin."""

    def banner(self):
        return f"[{self.name}] loaded"

class Upper(Plugin):
    @property
    def name(self):
        return "upper"

print(Upper().banner(), Plugin.__abstractmethods__)
```
```text
[upper] loaded frozenset({'name'})
```

### 16.4 `collections.abc`: abilities as classes

The module `collections.abc` defines ABCs for common **abilities**: `Iterable`, `Iterator`, `Sequence`, `Mapping`, `Callable` and more. They are the right tool for an `isinstance` check that respects duck typing:

```python
from collections.abc import Iterable, Mapping, Sequence

def describe(x):
    if isinstance(x, Mapping):
        return "mapping"
    if isinstance(x, Sequence):
        return "sequence"
    if isinstance(x, Iterable):
        return "iterable"
    return "single value"

for value in [{"a": 1}, [1, 2], "hi", {1, 2}, (n for n in "ab"), 42]:
    print(type(value).__name__, "->", describe(value))
```
```text
dict -> mapping
list -> sequence
str -> sequence
set -> iterable
generator -> iterable
int -> single value
```

Some of these ABCs check only for the right method. `Iterable` asks "does the class have `__iter__`?", so any class with an `__iter__` method (like the class-based iterators of core.10) counts as `Iterable`, even without inheriting from it.

### 16.5 `register`: virtual subclasses

You can tell an ABC "treat this class as one of yours" **without** inheritance, using `register`. The class becomes a **virtual subclass**: `isinstance` and `issubclass` say `True`, but it inherits nothing, and nothing is checked.

```python
from abc import ABC, abstractmethod

class Reader(ABC):
    @abstractmethod
    def read(self): ...

    def read_upper(self):
        return self.read().upper()

class OldTool:                    # written long ago; cannot change its bases
    def read(self):
        return "old data"

Reader.register(OldTool)
tool = OldTool()
print(isinstance(tool, Reader), issubclass(OldTool, Reader))
print(tool.read(), hasattr(tool, "read_upper"))
```
```text
True True
old data False
```

(`...` is the `Ellipsis` value, a common short body for abstract methods.) You will rarely need `register` yourself; it is how the standard library makes built-in types such as `tuple` count as a `Sequence`.

**ABC or duck typing?** In a small program, duck typing is usually enough. Use an ABC when you write a framework or library that others extend: it documents the required methods in one place and gives an early, clear error. Use `collections.abc` for checks that mean "has this ability" rather than "is exactly this class".


## 17. Custom exception classes and hierarchies

### 17.1 Exceptions are classes

Every exception you have met is a **class**, and they form an inheritance tree. You can see a part of it with the MRO:

```python
for cls in [ZeroDivisionError, FileNotFoundError, KeyError]:
    print([k.__name__ for k in cls.__mro__])
```
```text
['ZeroDivisionError', 'ArithmeticError', 'Exception', 'BaseException', 'object']
['FileNotFoundError', 'OSError', 'Exception', 'BaseException', 'object']
['KeyError', 'LookupError', 'Exception', 'BaseException', 'object']
```

This is why `except OSError` also catches `FileNotFoundError` (core.12): `except X` catches X **and all its subclasses**, exactly like `isinstance`. `Exception` is the base of all normal errors. Above it is `BaseException`, which also covers `KeyboardInterrupt` (Ctrl+C) and `SystemExit`. That is why you catch `Exception`, never `BaseException`, and why a bare `except:` is dangerous: it even swallows Ctrl+C.

### 17.2 Why define your own exceptions

Built-in exceptions such as `ValueError` are fine for simple checks. But when you write a **library** (code that other code uses), your own exception classes help the caller a lot:

- **Precise catching.** A caller can catch `ProductNotFound` and let other errors pass. With only `ValueError`, they cannot tell "product not found" from a bug that raised `ValueError` somewhere else.
- **Extra data.** The exception can carry attributes: which product, how many were asked for, how many are left. The caller does not need to parse the message text.
- **One net for everything.** If all your exceptions inherit from one base class, the caller can write `except ShopError` to catch every problem from your shop library, and only those.

### 17.3 Defining your own exceptions

The simplest custom exception inherits from `Exception` and has only a docstring as its body: `class InvalidSku(Exception): """The product code is not valid."""`. You raise it like any other: `raise InvalidSku(f"bad code: {text!r}")`. The message is stored in `e.args` and shown by `str(e)`. Name exception classes as nouns that describe the problem; many end in `Error` (`ValidationError`), but short names like `ProductNotFound` are also common.

When the caller needs **data** about the problem, add an `__init__` that stores it **and** passes a readable message to `super().__init__`:

```python
class OutOfStock(Exception):
    def __init__(self, item, requested, available):
        super().__init__(f"{item}: asked for {requested}, only {available} left")
        self.item = item
        self.requested = requested
        self.available = available

    @property
    def missing(self):
        return self.requested - self.available

try:
    raise OutOfStock("tea", requested=5, available=2)
except OutOfStock as e:
    print(e)
    print(e.item, e.requested, e.available, e.missing)
```
```text
tea: asked for 5, only 2 left
tea 5 2 3
```

Always call `super().__init__(message)`. If you forget, `str(e)` is empty and tracebacks show no message.

### 17.4 Designing a hierarchy

A good exception hierarchy for a library has **one base class**, then groups, then specific errors. Here is one for a small shop package:

```text
ShopError                         (base: "something went wrong in the shop")
├── NotFound                      (group: a thing does not exist)
│   ├── ProductNotFound
│   └── CustomerNotFound
└── OrderError                    (group: an order rule was broken)
    ├── OutOfStock
    └── PaymentDeclined
```

```python
class ShopError(Exception):
    """Base class for every error raised by the shop package."""

class NotFound(ShopError):
    pass

class ProductNotFound(NotFound):
    def __init__(self, sku):
        super().__init__(f"no product with code {sku}")
        self.sku = sku

class OrderError(ShopError):
    pass

class PaymentDeclined(OrderError):
    pass

def find(sku):
    raise ProductNotFound(sku)

try:
    find("T-99")
except NotFound as e:
    print(type(e).__name__, e.sku, e)
print(issubclass(ProductNotFound, ShopError), issubclass(PaymentDeclined, NotFound))
```
```text
ProductNotFound T-99 no product with code T-99
True False
```

Callers choose how precise to be: `except ProductNotFound`, `except NotFound`, or `except ShopError`. Section 20 designs the same kind of tree for a library system. Guidelines:

- **Inherit from `Exception`** (or from a fitting built-in such as `ValueError` or `LookupError`, if your error really is one; then old code that catches `ValueError` still works).
- **Keep it shallow.** Two or three levels are plenty. Create a class only if some caller would want to catch it separately.
- **Put the data in attributes**, the explanation in the message.
- **Document** which methods raise which exceptions.

### 17.5 Catch order: specific first

`except` clauses are tried **from top to bottom**, and the **first** one that matches wins. A general class placed first catches everything below it, and the specific clause never runs:

```python
try:
    find("X-1")
except ShopError:
    print("general handler ran")
except ProductNotFound:
    print("never reached")
```
```text
general handler ran
```

So: most specific classes first, the base class last. (Linters warn about the order above.)

### 17.6 Never a bare `except`, and do not hide errors

A bare `except:` (or an `except Exception:` that only prints "something failed") hides bugs: a `NameError` from a typo looks exactly like "the product is out of stock". Catch the **specific** exceptions you know how to handle, and let the rest propagate. If you must catch broadly (for example at the very top of a program, to log and exit), log the full error and re-raise or exit with an error code.

### 17.7 Predict the output

```python
class ShopError(Exception): pass
class PaymentError(ShopError): pass
class CardDeclined(PaymentError): pass

def run(exc):
    try:
        raise exc
    except CardDeclined:
        return "declined"
    except ShopError as e:
        return f"shop:{type(e).__name__}"
    except Exception:
        return "other"

print(run(CardDeclined()), run(PaymentError()), run(ShopError()), run(KeyError("k")))
```

<details><summary>Answer</summary>

```text
declined shop:PaymentError shop:ShopError other
```

Each exception goes to the first clause that matches it. `PaymentError` is not a `CardDeclined`, but it is a `ShopError`. `KeyError` is not part of our hierarchy, so only `except Exception` catches it.
</details>

## 18. Exception chaining

### 18.1 Translating an exception

Inside your library, a low-level error happens: `int()` raises `ValueError`, a `dict` lookup raises `KeyError`. Your caller should not need to know these details; they expect your own exception, such as `OrderError`. So you catch the low-level error and raise your own. But the original error contains valuable information for debugging. **Exception chaining** keeps both.

```python
class OrderError(Exception):
    pass

def parse_quantity(text):
    try:
        quantity = int(text)
    except ValueError as e:
        raise OrderError(f"quantity must be a whole number, got {text!r}") from e
    return quantity

parse_quantity("3kg")
```
```text
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 10: '3kg'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ...
OrderError: quantity must be a whole number, got '3kg'
```

`raise NewError(...) from original` sets `NewError.__cause__ = original`. The traceback shows **both**, oldest first, joined by the line "The above exception was the direct cause of the following exception". Read chained tracebacks **from the bottom up**: the last error is the one that reached you; above it is its cause.

### 18.2 Implicit chaining: `__context__`

If an exception happens **while handling another one** and you did not use `from`, Python still links them, but it sets `__context__` and prints a different line:

```python
def load(settings):
    try:
        return settings["port"]
    except KeyError:
        return int(settings["default_port"])   # a bug while handling

load({"default_port": "eighty"})
```
```text
Traceback (most recent call last):
  ...
KeyError: 'port'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 10: 'eighty'
```

The two linking lines mean different things:

| Line in the traceback | Attribute | Meaning |
|---|---|---|
| "The above exception was the direct cause of the following exception" | `__cause__` | you wrote `raise ... from e`: **on purpose** |
| "During handling of the above exception, another exception occurred" | `__context__` | a new error happened inside an `except` block: often **a bug** in the handler |

So when you translate an exception on purpose, always use `from e`. Then readers of the traceback know it was deliberate.

### 18.3 Looking at the attributes

```python
def demo(mode):
    try:
        try:
            {}["missing"]
        except KeyError as e:
            if mode == "from":
                raise ValueError("translated") from e
            if mode == "from None":
                raise ValueError("translated") from None
            raise ValueError("translated")
    except ValueError as err:
        return (type(err.__cause__).__name__, type(err.__context__).__name__,
                err.__suppress_context__)

for mode in ["implicit", "from", "from None"]:
    print(mode, demo(mode))
```
```text
implicit ('NoneType', 'KeyError', False)
from ('KeyError', 'KeyError', True)
from None ('NoneType', 'KeyError', True)
```

- **Implicit**: `__cause__` is `None` (shown as `NoneType`), `__context__` is the `KeyError`.
- **`from e`**: both are set; `__suppress_context__` is `True`, so only the cause is printed.
- **`from None`**: `__cause__` is `None`, `__context__` is still recorded, but `__suppress_context__` is `True`, so the traceback **hides** the old error.

### 18.4 `from None`: hide an irrelevant detail

Use `from None` when the original error is just noise for the user, for example a `KeyError` that you turned into a clear message:

```python
class UnknownCommand(Exception):
    pass

COMMANDS = {"add": 1, "list": 2}

def lookup(name):
    try:
        return COMMANDS[name]
    except KeyError:
        raise UnknownCommand(f"unknown command {name!r}; try: add, list") from None

lookup("dlete")
```
```text
Traceback (most recent call last):
  ...
UnknownCommand: unknown command 'dlete'; try: add, list
```

Only the clean message is shown. Use it sparingly: if the original error could ever help debugging, keep it with `from e`.

### 18.5 Adding a note: `add_note`

Sometimes you do not want a new exception; you want to add **context** to the existing one and let it continue. `e.add_note(text)` attaches extra lines that the traceback prints after the message:

```python
def parse_rows(lines):
    result = []
    for number, line in enumerate(lines, start=1):
        try:
            result.append(int(line))
        except ValueError as e:
            e.add_note(f"while reading line {number}: {line!r}")
            raise
    return result

parse_rows(["10", "20", "x3"])
```
```text
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 10: 'x3'
while reading line 3: 'x3'
```

The bare `raise` re-raises the same exception, now with a note. The notes are stored in the list `e.__notes__`. This is handy in loops: the error type stays the same, so callers' `except ValueError` still works, but the message says where it happened.

## 19. Exception groups and `except*`

### 19.1 Why one exception is not always enough

A normal `raise` reports **one** problem. Sometimes there are several independent failures at once:

- a form with five fields, and three of them are invalid: the user wants **all three** messages, not one at a time;
- ten tasks running, and two of them failed;
- cleaning up five resources, and two clean-ups failed.

Python 3.11 added **`ExceptionGroup`**: one exception that **contains** a list of exceptions.

```python
def check_product(product):
    problems = []
    if not product.get("name"):
        problems.append(ValueError("name is required"))
    if not isinstance(product.get("price"), int):
        problems.append(TypeError("price must be an int"))
    if not product.get("sku", "").startswith("P-"):
        problems.append(ValueError("sku must start with P-"))
    if problems:
        raise ExceptionGroup("invalid product", problems)

check_product({"name": "", "price": "20", "sku": "x"})
```
```text
  + Exception Group Traceback (most recent call last):
  |   ...
  | ExceptionGroup: invalid product (3 sub-exceptions)
  +-+---------------- 1 ----------------
    | ValueError: name is required
    +---------------- 2 ----------------
    | TypeError: price must be an int
    +---------------- 3 ----------------
    | ValueError: sku must start with P-
    +------------------------------------
```

`ExceptionGroup(message, list_of_exceptions)` takes a message and a **non-empty** list. The traceback draws the group as a box with each sub-exception numbered. The class name `ExceptionGroup` is built in; you do not import it.

### 19.2 Looking inside a group

```python
try:
    check_product({"name": "", "price": "20", "sku": "x"})
except ExceptionGroup as eg:
    print(eg.message)
    print(len(eg.exceptions), [type(e).__name__ for e in eg.exceptions])
    for e in eg.exceptions:
        print(" -", e)
```
```text
invalid product
3 ['ValueError', 'TypeError', 'ValueError']
 - name is required
 - price must be an int
 - sku must start with P-
```

A plain `except ExceptionGroup` catches the whole group as one object. `eg.message` is the text, `eg.exceptions` is a tuple of the members.

Groups can be **nested**: a member can itself be a group. This happens naturally when tasks run sub-tasks:

```python
inner = ExceptionGroup("row 2", [ValueError("bad price"), KeyError("sku")])
outer = ExceptionGroup("import failed", [inner, TypeError("bad header")])
print(outer)
print([type(e).__name__ for e in outer.exceptions])
```
```text
import failed (2 sub-exceptions)
['ExceptionGroup', 'TypeError']
```

`print(outer)` shows the message and the number of **direct** members: the inner group counts as one.

### 19.3 `split` and `subgroup`

A group has two methods to take it apart **by type**, keeping the nested structure:

- `eg.subgroup(T)` returns a new group with only the members that are instances of `T` (searching inside nested groups), or `None` if there are none.
- `eg.split(T)` returns a pair `(match, rest)`: the matching part and the non-matching part. Each part is a group or `None`.

```python
match, rest = outer.split(ValueError)
print(repr(match))
print(repr(rest))
print(repr(outer.subgroup(KeyError)))
print(outer.subgroup(ZeroDivisionError))
```
```text
ExceptionGroup('import failed', [ExceptionGroup('row 2', [ValueError('bad price')])])
ExceptionGroup('import failed', [ExceptionGroup('row 2', [KeyError('sku')]), TypeError('bad header')])
ExceptionGroup('import failed', [ExceptionGroup('row 2', [KeyError('sku')])])
None
```

Look carefully at the structure: `match` still has the outer message `"import failed"` and the inner group `"row 2"`, but each now holds only the matching members. Empty inner groups disappear. The original `outer` is not changed. `T` can also be a tuple of types, or a function that takes an exception and returns `True` or `False`.

### 19.4 `except*`: handle each kind of member

`except*` (read "except star") is a new form of `except` made for groups. Each `except*` clause handles the **members of one type**, and several clauses can run for **one** group:

```python
def handle(eg):
    try:
        raise eg
    except* ValueError as e:
        print("ValueError part:", repr(e))
    except* TypeError as e:
        print("TypeError part:", repr(e))

handle(ExceptionGroup("invalid", [ValueError("a"), TypeError("b"), ValueError("c")]))
```
```text
ValueError part: ExceptionGroup('invalid', [ValueError('a'), ValueError('c')])
TypeError part: ExceptionGroup('invalid', [TypeError('b')])
```

Both clauses ran, and each got only its part. Here are the **exact rules** of a `try` with `except*`:

1. The raised exception is the **unhandled part**. (If it is a plain exception, not a group, Python first wraps it in a group, so the same rules apply.)
2. The clauses are tried **from top to bottom**. For each clause, Python does `match, rest = unhandled.split(T)` with that clause's type `T`.
3. If `match` is not `None`, the clause runs **once**, with `e` bound to `match`. **`e` is always an `ExceptionGroup`**, even if it holds a single exception. The unhandled part becomes `rest`.
4. If `match` is `None`, the clause is skipped.
5. **Each clause runs at most once**, no matter how many members match it.
6. When all clauses are done, if anything is still unhandled, Python **re-raises it** as a group (with the original message). Exceptions raised **inside** the clauses are added to what is re-raised.

Watch rule 6, the leftover part, in action:

```python
try:
    try:
        raise ExceptionGroup("batch", [ValueError("v"), KeyError("k"), OSError("disk")])
    except* ValueError as e:
        print("handled", [str(x) for x in e.exceptions])
    except* KeyError as e:
        print("handled", [repr(x) for x in e.exceptions])
except ExceptionGroup as leftover:
    print("still raised:", repr(leftover))
```
```text
handled ['v']
handled ["KeyError('k')"]
still raised: ExceptionGroup('batch', [OSError('disk')])
```

The `OSError` matched no clause, so the inner `try` re-raised a group containing only it, still called `"batch"`. The outer `try` caught that.

A plain exception is wrapped, so `e` is a group, not the exception itself:

```python
try:
    int("x")
except* ValueError as e:
    print(type(e).__name__, repr(e.exceptions[0]))
```
```text
ExceptionGroup ValueError("invalid literal for int() with base 10: 'x'")
```

And `except*` looks **inside nested groups** (that is what `split` does):

```python
def show(outer):
    try:
        raise outer
    except* KeyError as e:
        print("KeyError part:", repr(e))
    except* (ValueError, TypeError) as e:
        print("Value/Type part:", repr(e))

inner = ExceptionGroup("row 2", [ValueError("bad price"), KeyError("sku")])
show(ExceptionGroup("import failed", [inner, TypeError("bad header")]))
```
```text
KeyError part: ExceptionGroup('import failed', [ExceptionGroup('row 2', [KeyError('sku')])])
Value/Type part: ExceptionGroup('import failed', [ExceptionGroup('row 2', [ValueError('bad price')]), TypeError('bad header')])
```

### 19.5 Rules about mixing and limits

- You **cannot mix** `except` and `except*` in the same `try` statement. It is a `SyntaxError`, found before anything runs:

```python
try:
    pass
except ValueError:
    pass
except* TypeError:
    pass
```

```text
SyntaxError: cannot have both 'except' and 'except*' on the same 'try'
```

(This is the message Python 3.14 prints for the code above, with the file and line trimmed.)

- `except* ExceptionGroup` is not allowed (a `TypeError` at run time): the clauses are for the **member** types. To catch a whole group as one object, use a plain `except ExceptionGroup`.
- Inside an `except*` clause you cannot use `return`, `break` or `continue`. The other clauses may still need to run, so jumping out is forbidden. Set a variable instead, and return after the `try`.
- A plain `except ValueError` does **not** catch a group that contains a `ValueError`. The group is an `ExceptionGroup`, not a `ValueError`. That is exactly why `except*` exists.

### 19.6 When to use exception groups

Use them when **several independent errors** really happen together: many fields, many tasks, many clean-ups. (Concurrency tools such as `asyncio.TaskGroup`, met later, raise them.) For a single problem, raise one normal exception. If your function can raise a group, say so in its docstring, because callers must use `except*` or `except ExceptionGroup`.

### 19.7 Predict the output

```python
def check():
    try:
        raise ExceptionGroup("g", [
            ValueError(1),
            ExceptionGroup("inner", [TypeError(2), ValueError(3)]),
            KeyError(4),
        ])
    except* ValueError as e:
        print("A", repr(e))
    except* (TypeError, ValueError) as e:
        print("B", repr(e))

try:
    check()
except ExceptionGroup as rest:
    print("C", repr(rest))
```

<details><summary>Answer</summary>

```text
A ExceptionGroup('g', [ValueError(1), ExceptionGroup('inner', [ValueError(3)])])
B ExceptionGroup('g', [ExceptionGroup('inner', [TypeError(2)])])
C ExceptionGroup('g', [KeyError(4)])
```

- Clause A takes **all** `ValueError`s, at every level: `1` at the top, `3` inside `"inner"`.
- Clause B also mentions `ValueError`, but those are already handled; it gets only the `TypeError`. Each clause sees only what earlier clauses left.
- `KeyError(4)` matched nothing, so it is re-raised in a group still called `"g"`, and the caller prints it as C.
</details>


## 20. Project: a library management system

Problem `core.14.p070` asks you to build a small library system. This section walks through the **design**: which classes, what each one owns, which exceptions, and why. It shows the key pieces but leaves the full code to you.

### 20.1 The requirements

A library has **books** (each with an ISBN, a title, and a number of copies) and **members** (each with an id, a name, and a loan limit). A member can **check out** a book if a copy is free and they have not reached their limit. A loan lasts 14 days. A member **returns** a book. The library can list **overdue** loans for a given day. Days are simple integers (day 1, day 2, ...), so you do not need dates. Every problem must raise a clear library exception.

### 20.2 From nouns to classes

Underline the nouns: *library, book, member, loan, day*. The first four have data **and** rules, so they become classes. A day is just a number.

| Class | Data | Responsibilities |
|---|---|---|
| `Book` | `isbn`, `title`, `copies`, `on_loan` | knows how many copies are free (a read-only property `available`) |
| `Member` | `member_id`, `name`, `limit`, `loans` | knows if it can borrow more (`can_borrow()`) |
| `Loan` | `book`, `member`, `start_day`, `due_day` | knows if it is overdue on a given day (`is_overdue(day)`) |
| `Library` | `books` (dict by ISBN), `members` (dict by id), `loans` (list) | the public interface: `add_book`, `add_member`, `checkout`, `return_book`, `overdue(day)` |

Each class guards its own rules. `Book` never lets `on_loan` go above `copies`; `Loan` computes `due_day` once in `__init__`. The `Library` coordinates: it finds the objects and calls their methods.

### 20.3 Composition, not inheritance

Ask the sentences from section 14. "A library **is a** book"? No. "A library **has** books and members"? Yes: composition. "A loan **is a** book"? No: a loan **refers to** a book and a member. So `Loan` stores the two objects as attributes. Nothing here inherits from anything except the exceptions, and that is normal: real domain models use far more composition than inheritance.

Should `Library` inherit from `dict` to store books? No, for the reason of section 14.2: users could then call `library.clear()` or put anything under any key. Keep the dictionaries as internal attributes (`self._books`), and offer methods.

### 20.4 The exception hierarchy

Callers want to catch "anything that went wrong in the library" **or** one exact problem. So: one base class, and specific subclasses that carry data.

```text
LibraryError
├── BookNotFound          (isbn)
├── MemberNotFound        (member_id)
├── BookUnavailable       (isbn)
└── LoanLimitReached      (member_id, limit)
```

A key piece: the base class and one specific error with data, plus the helper that **translates** the low-level `KeyError` with chaining (section 18):

```python
class LibraryError(Exception):
    """Base class for every error raised by the library system."""

class BookNotFound(LibraryError):
    def __init__(self, isbn):
        super().__init__(f"no book with ISBN {isbn}")
        self.isbn = isbn

class Library:
    def __init__(self):
        self._books = {}

    def _get_book(self, isbn):
        try:
            return self._books[isbn]
        except KeyError as e:
            raise BookNotFound(isbn) from e

lib = Library()
try:
    lib._get_book("978-81")
except LibraryError as err:
    print(type(err).__name__, err.isbn, repr(err.__cause__))
lib._get_book("978-81")
```
```text
BookNotFound 978-81 KeyError('978-81')
Traceback (most recent call last):
  ...
KeyError: '978-81'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ...
BookNotFound: no book with ISBN 978-81
```

The caller catches `LibraryError` (or `BookNotFound`) and gets the ISBN as data. A developer reading the traceback still sees the original `KeyError` as the direct cause. Write `MemberNotFound` and `_get_member` the same way. Should `BookNotFound` be `from e` or `from None`? Here the `KeyError` adds little, so both are defensible; the problem's tests tell you which one they expect.

### 20.5 The checkout steps

Write `checkout(member_id, isbn, day)` as a list of steps, each of which either succeeds or raises:

1. `member = self._get_member(member_id)`: may raise `MemberNotFound`.
2. `book = self._get_book(isbn)`: may raise `BookNotFound`.
3. If the member cannot borrow more: raise `LoanLimitReached`.
4. If the book has no free copy: raise `BookUnavailable`.
5. Only now **change state**: create the `Loan`, add it to the library's list and the member's list, and increase `book.on_loan`. Return the loan.

The order matters. **Check everything first, change state last.** If you increased `on_loan` before checking the member's limit, a failed checkout would leave the book counted as lent. `return_book` follows the same pattern: find the loan (or raise a `LibraryError` subclass), then undo the three changes.

### 20.6 The overdue report and the finishing touches

`overdue(day)` is a short list comprehension over the loans that asks each loan `loan.is_overdue(day)`. The library does not compute dates itself; the loan knows its own rule. That is encapsulation at work: if the loan period changes, only `Loan` changes.

Give each class a simple `__repr__` (section 4.4), so that test failures print `Loan('978-81', 'M1', due=15)` instead of an address. Use `_` names for internal dictionaries. Use a class attribute for the loan period (`Loan.PERIOD = 14`), because it is shared by all loans and never changes per loan.

### 20.7 Your turn

Problem `core.14.p070` gives the exact method names, messages and attributes that the tests expect. Build it class by class: `Book` and its tests first, then `Member`, then `Loan`, then the exceptions, and `Library` last. Ideas to extend it afterwards: a fine per overdue day; a `ReferenceBook(Book)` subclass that can never be lent (is inheritance right here? what about `BookUnavailable`?); and a `check_all()` method that validates every member and raises an `ExceptionGroup` with one error per broken rule (section 19).

## 21. Common traps

The section number tells you where each trap was explained.

1. **Forgetting `self`** in a method definition (3.3): "takes 0 positional arguments but 1 was given". Or forgetting `self.` inside a method, which reads a global or raises `NameError`.
2. **Setting attributes outside `__init__`** (2.2, 4.3), so some objects lack them: `AttributeError` later.
3. **A mutable class attribute** (5.4): one list shared by every instance. Create lists, dicts and sets in `__init__`.
4. **A mutable default argument** in `__init__` (4.3): use `None` and create the value inside.
5. **`self.counter += 1` for a class-level counter** (5.3): it creates an instance attribute. Use `ClassName.counter` or `type(self).counter`.
6. **Hard-coding the class name** in an alternative constructor (6.3): subclasses get the wrong type. Return `cls(...)`.
7. **Using `__name` "for privacy"** (7.3): it is only mangled, not hidden. Use one underscore.
8. **A setter that assigns to its own property name** (8.2): `RecursionError`. Store the value in `self._name`.
9. **Forgetting `super().__init__(...)`** in a subclass `__init__` (11.2): the parent's attributes are missing.
10. **Calling parents by name in a diamond** (12.8): the shared base runs twice. Use `super()` everywhere, with `**kwargs`.
11. **Thinking `super()` means "my parent"** (12.7): it means "the next class in the MRO of the object".
12. **Wrong base order**, mixin last (13.3), or a parent before its child (12.6): the mixin never runs, or `TypeError: Cannot create a consistent method resolution order`.
13. **Inheriting to reuse code** when the "is-a" sentence is false (14.2): `Stack(list)` leaks 40 methods. Prefer composition.
14. **A wide `try` around a duck-typed call** (15.3, 15.5): it hides bugs inside the method.
15. **A general `except` before a specific one** (17.5): the specific clause never runs. Specific first.
16. **A custom exception without `super().__init__(message)`** (17.3): `str(e)` is empty.
17. **Raising a new exception inside `except` without `from`** (18.2): the traceback says "During handling..." and looks like a bug. Use `raise ... from e`.
18. **Catching a group with plain `except ValueError`** (19.5): it does not match. Use `except*`. And never mix `except` and `except*` in one `try`.

## 22. Summary

- A **class** is a blueprint; calling it makes an **instance**. Instances hold data in their `__dict__`; the class holds the methods. `vars(obj)` shows the instance's attributes.
- A **method** is a function in the class. `obj.method(x)` is `Class.method(obj, x)`: Python makes a **bound method** and passes the instance as `self`. Functions stored on an instance are not bound.
- **`__init__`** fills in a new object right after it is created. Set every attribute there, validate the arguments, and never use mutable defaults. A simple **`__repr__`** makes objects print usefully (core.15 has the full data model).
- **Class attributes** are shared. Reading looks in the instance first, then the class; **assignment always writes to the instance** and shadows the class value. Keep class attributes immutable.
- **`@classmethod`** receives `cls` and is ideal for alternative constructors (`return cls(...)`). **`@staticmethod`** receives nothing special.
- **`_name`** means internal. **`__name`** is **mangled** to `_Class__name` to avoid clashes in subclasses; it is not security.
- A **property** looks like an attribute but runs a getter, setter or deleter. Use it for validation, computed values and read-only attributes, with a backing attribute such as `_price`.
- **Lookup order**: a property on the class wins, then the instance `__dict__`, then the class and its parents in MRO order, else `AttributeError`.
- **Inheritance** models "is-a". Subclasses **override** and **extend**; a base class can call `self.hook()` that subclasses fill in. `isinstance` respects inheritance; test the most specific class first.
- **`super()`** calls the next class in the **MRO**. In a subclass `__init__`, call `super().__init__(...)` first.
- The **MRO** comes from **C3 linearization**: `L[X] = X + merge(L[parents]..., [parents])`; take the first head that is in no list's tail. Children come before parents, and the written base order is kept. If no order exists, `class` raises `TypeError`. Check with `Cls.__mro__`.
- **Cooperative** multiple inheritance: every class calls `super()`, and `__init__` takes keyword arguments plus `**kwargs`. Then each class in a diamond runs once.
- **Mixins** add one behaviour, have no `__init__`, are named `...Mixin`, go left of the main base, and call `super()` when they override.
- **Composition** models "has-a" and lets you hide details and swap parts (strategies). Prefer it when the "is-a" sentence is not always true.
- **Duck typing**: what an object can do matters, not its class. Prefer **EAFP** with a small `try`. Use `isinstance` with ABCs for abilities.
- **ABCs** (`abc.ABC`, `@abstractmethod`) refuse to instantiate until all abstract methods are implemented; `Cls.__abstractmethods__` lists the missing ones. `collections.abc` describes abilities; `register` creates virtual subclasses.
- **Custom exceptions**: one base class per library, a few specific subclasses, data in attributes, message via `super().__init__`. Catch specific classes first; never use a bare `except`.
- **Chaining**: `raise New(...) from e` sets `__cause__` ("direct cause"); raising inside `except` without `from` sets `__context__` ("during handling"); `from None` hides the old error. `e.add_note(...)` adds context to an existing exception.
- **`ExceptionGroup(msg, [errors])`** reports several errors at once; `split` and `subgroup` take it apart by type. Each **`except*`** clause runs at most once with the matching sub-group; whatever is left is re-raised. `except` and `except*` cannot be mixed in one `try`.

When you can turn a real description into classes with clear responsibilities, choose composition or inheritance with the "is-a / has-a" test, design an exception tree that callers can catch at the right level, and compute a diamond's MRO on paper before Python prints it, you have met the outcomes of this module. The problems that follow practise each part.

### What comes next

In **core.15, the Python data model**, your classes learn to behave like built-in types: to compare with `==` and `<`, to work with `len()`, `[]`, `in` and `for`, to be used in `with` blocks, and to be written in a few lines with dataclasses.
