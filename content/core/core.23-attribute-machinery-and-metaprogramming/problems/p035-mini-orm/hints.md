## Hint 1

Build it in layers, running one test group at a time:

1. **Fields alone** (`pytest -k TestFieldDescriptors`). A field is a data descriptor like the
   validators of this chapter. Which method runs on `u.age = "old"`? Where does each user's
   value live so two users do not share it? What should `__get__` return when `obj is None`?
2. **Model setup** (`-k TestModelDefinition`). `__init_subclass__` runs once per model class,
   after every `__set_name__`. How do you get the parent's fields? (Normal lookup of
   `cls._fields` finds the nearest parent's dict; copy it, never change it in place.) If you add
   the automatic `id` with `setattr` after the class exists, who calls its `__set_name__`?
3. **SQL text** (`-k TestCreateTable`). Build strings from `cls._fields` only: they are names
   you control.
4. **save/get/filter/delete**. For each query write two things side by side: the SQL text with
   `?` marks, and the list of values in the same order.

## Hint 2

```
Field.__set__(obj, value):
    validate(value, type(obj).__name__)      # ValueError for bad None, TypeError for bad type
    obj.__dict__[self.name] = value

Model.__init_subclass__(cls):
    fields = dict(cls._fields)               # parent's, copied
    for name, value in vars(cls).items(): if value is a Field: fields[name] = value
    pks = names of fields with primary_key
    if more than one: TypeError
    if none: pk = IntegerField(primary_key=True); pk.__set_name__(cls, "id"); setattr(cls, "id", pk)
             fields = {"id": pk, **fields}
    cls._fields, cls._pk = fields, the key name
    if "table_name" not in vars(cls): cls.table_name = cls.__name__.lower()
    if not cls.table_name.isidentifier(): TypeError

save(conn):
    check required fields are not None (before any SQL)
    others = [names except the key]
    if key value is not None:
        cur = execute("UPDATE t SET a = ?, b = ? WHERE pk = ?", [a, b, key])
        if cur.rowcount == 0: execute("INSERT INTO t (pk, a, b) VALUES (?, ?, ?)", [key, a, b])
    else:
        cur = execute("INSERT INTO t (a, b) VALUES (?, ?)", [a, b]);  set key = cur.lastrowid

filter(conn, **criteria):
    for each name, value: unknown name -> TypeError
        None  -> "name IS NULL"         (no parameter)
        other -> "name = ?" and params.append(value)
    "SELECT cols FROM t" + (" WHERE " + " AND ".join(parts) if parts) + " ORDER BY pk"
    build objects with cls(**dict(zip(cls._fields, row)))
```
