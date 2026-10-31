- Using `__import__("toolbox.sub.maths")`. It returns the **top** package `toolbox`, not `maths`.
  `importlib.import_module` returns the module you asked for.
- Calling `getattr(module, "text.shout")`. `getattr` takes one name; a dotted string is looked up as
  a single (missing) name. Split on `.` and loop.
- Catching every exception around the import and raising a vague error. The user then cannot see
  which import inside their module failed.
- Calling the object inside `resolve`. An entry point can point at a constant or a module too;
  `resolve` only finds it.
- Importing every target in the table up front. One broken entry would break every command.
