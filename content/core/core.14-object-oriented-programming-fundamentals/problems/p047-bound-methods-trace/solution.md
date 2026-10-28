## Approach

Do the lookup by hand for every attribute: first the instance `__dict__`, then the class (and its
parents). Then ask what kind of object was found. A function on the class is bound to the instance;
a function in the instance dict is not; a `staticmethod` is never bound; a `classmethod` is bound to
the class. (Chapter sections 3, 6 and 9.)

## Step by step

1. `a.greet("Ben")` is `Greeter.greet(a, "Ben")`: `self.greeting` is the class attribute `"Hi"`,
   `self.name` is `"Asha"` -> `Hi Ben, I am Asha`.
2. `Greeter.greet(b, "Asha")`: through the class you get the plain function, so you pass `self`
   yourself. `self` is `b` -> `Hi Asha, I am Ben`.
3. `m = a.greet` makes a bound method object. It stores the **object** `a` (in `m.__self__`) and the
   function (in `m.__func__`), not a copy of `a.name`. After `a.name = "Asha K"`, `m("Cy")` reads the
   new name -> `Hi Cy, I am Asha K`.
4. `m.__self__ is a` -> `True`; `m.__func__ is Greeter.greet` -> `True` (the same function object
   that lives in the class).
5. `a.wave = wave` puts a plain function in `a.__dict__`. It is **not** bound, so
   `a.wave("hello")` is `wave("hello")` -> `wave(str)`.
6. `a.wave()` is `wave()` with no argument -> `TypeError` is caught -> `TypeError`.
7. `Greeter.wave = wave` puts the same function on the class. `b` has no own `wave`, so `b.wave()`
   finds the class function and binds it: `wave(b)` -> `wave(Greeter)`.
8. `a.wave(3)`: `a` still has its **own** `wave`, and the instance dict wins over a normal method
   on the class. Not bound -> `wave(3)` -> `wave(int)`.
9. After `del a.wave` only the class function is left, so `a.wave()` is `wave(a)` ->
   `wave(Greeter)`.
10. `staticmethod` is never bound, through an instance or the class: `HEY! HO!`.
11. `classmethod` is bound to the class, also when called through an instance: `Greeter Greeter`.
12. `c.kind()` binds `cls` to the class of `c`, which is `Loud`; `c.shout("ok")` -> `OK!`:
    `Loud OK!`.
13. `c.greet("you")`: `self.greeting` is found on `Loud` first -> `HELLO you, I am Cy`.
14. `f = Greeter.greet` is the plain function. `f(c, "me")` passes `c` as `self`, and
    `self.greeting` is again looked up on `c` -> `HELLO me, I am Cy`. Where `f` came from does not
    matter; only `self` does.
15. `a.greet` is a bound method (`method`); `Greeter.greet` is a plain `function`; `a.shout` is
    the plain function inside the `staticmethod` -> `method function function`.

## Output

```text
Hi Ben, I am Asha
Hi Asha, I am Ben
Hi Cy, I am Asha K
True True
wave(str)
TypeError
wave(Greeter)
wave(int)
wave(Greeter)
HEY! HO!
Greeter Greeter
Loud OK!
HELLO you, I am Cy
HELLO me, I am Cy
method function function
```

## Complexity

Not applicable.

## Another way

Check your answers in the REPL with `vars(a)` (what the instance owns), `vars(Greeter)` (what the
class owns) and `type(a.wave)`. If you want a function in the instance to behave like a method,
do not store it in the instance: put it on the class, or pass the object yourself.
