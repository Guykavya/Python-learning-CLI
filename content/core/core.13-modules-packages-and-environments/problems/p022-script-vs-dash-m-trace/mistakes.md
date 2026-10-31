- Writing `__package__ = 'app'` for command 1. A file run by path has no package; `__package__` is `None`.
- Printing `app package loaded` in command 1. Nothing imports `app` there.
- Writing `helpers loaded as app.helpers` in command 1. The plain `import helpers` finds the file through
  `sys.path[0]` (the `app/` folder) and names the module `helpers`.
- In command 2, putting `relative import worked` before `helpers loaded as app.helpers`. The module's
  code runs during the import statement, before the next line.
- Thinking `__name__` is `app.main` with `-m`. The module you run is always `__main__`.
