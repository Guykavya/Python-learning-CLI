# Project: a Mini ORM with descriptors

An **ORM** (object-relational mapper, like Django's models or SQLAlchemy) lets you write

```python
class User(Model):
    name = TextField(max_length=40)
    email = TextField(null=True)
    age = IntegerField(default=18)

ann = User(name="Ann", age=30).save(conn)     # INSERT, ann.id is now 1
ann.age = 31                                   # validated on assignment
ann.save(conn)                                 # UPDATE
User.filter(conn, age=31)                      # [User(id=1, name='Ann', email=None, age=31)]
```

and never write SQL by hand. Under the hood it is exactly this chapter: every field is a
**data descriptor** that validates on assignment and learns its name with `__set_name__`, and
the base class collects the fields of each model in `__init_subclass__`. This is the module
project; make it clean, because you will reuse the ideas.

Copy `starter.py` to `solution.py` and complete it. The tests use `sqlite3.connect(":memory:")`
wrapped in a small spy object, so **run every query with `conn.execute(sql, params)`** (no
cursors, no `executescript`) and use `?` placeholders.

## Part 1: fields

`Field(*, primary_key=False, null=False, default=None)` is a data descriptor:

- `__set_name__` stores the attribute name in `self.name`.
- `Model.field` (read through the class) returns the descriptor. Reading a field that was never
  set returns `default`. Values live in the **instance** `__dict__` under the field's name.
- Every assignment is validated (also the ones made by `__init__`). `ClassName` below is
  `type(obj).__name__`:
  - `None` is allowed only if `null=True` or for the primary key; otherwise `ValueError` whose
    message contains `ClassName.field` (for example `User.name cannot be None`).
  - A value of the wrong type raises `TypeError` whose message contains `ClassName.field`
    (`User.age must be int, got str`). `bool` is **not** accepted as an integer.
  - A rejected value is not stored.
- `IntegerField` (`sql_type = "INTEGER"`, accepts `int`) and `TextField` (`sql_type = "TEXT"`,
  accepts `str`, plus an optional `max_length`: a longer string raises `ValueError` naming the field).

## Part 2: models

`Model.__init_subclass__` sets up each model class:

- `cls._fields`: a dict from field name to `Field`, in **column order**: inherited fields first,
  then the class's own fields in definition order. Find fields by scanning `vars(cls)` for
  `Field` objects. **Do not use `__annotations__`** (fields need no type hints, and on Python 3.14
  annotations are evaluated lazily).
- Primary key: at most one field may have `primary_key=True` (more raise `TypeError`). If there is
  none, add `id = IntegerField(primary_key=True)` as the **first** column. Remember that
  `__set_name__` is only called automatically while the class is being created.
- `cls._pk`: the name of the primary key field.
- `table_name`: if the class body does not set it, it is the class name in lower case
  (`User` → `user`), also for subclasses (`Admin(User)` → `admin`). It must be a valid Python
  identifier (`str.isidentifier`), otherwise `TypeError`: table and column names cannot be
  `?` parameters, so the ORM only ever puts trusted identifiers into SQL text.
- `Model.__init__(**values)` assigns each value through its field; an unknown name raises `TypeError`.

## Part 3: SQL

| Method | Behaviour |
|---|---|
| `create_table_sql()` (classmethod) | `CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, age INTEGER NOT NULL)`: one `name TYPE` per field in column order, `PRIMARY KEY` for the key, `NOT NULL` for other fields without `null=True` |
| `create_table(conn)` (classmethod) | executes `create_table_sql()` |
| `save(conn)` | First checks that no non-null field (other than the key) is `None`, else `ValueError` naming it, before any SQL. If the key is `None` and it is an `IntegerField`: `INSERT` the other columns and set the key from `cursor.lastrowid`. If the key is `None` and not an integer field: `ValueError`. If the key is set: `UPDATE ... WHERE key = ?`; if that changed no row (`cursor.rowcount == 0`), `INSERT` the row including its key. Returns `self` |
| `delete(conn)` | `DELETE` this row and set the key back to `None`; `ValueError` if the key is `None` |
| `get(conn, pk_value)` (classmethod) | the object with that key, or `None` |
| `filter(conn, **criteria)` (classmethod) | a list of objects whose columns equal all criteria (joined with `AND`), ordered by the key. No criteria: all rows. A `None` criterion means `column IS NULL`. An unknown field name raises `TypeError` |

Every **value** goes into `params`; the SQL text contains only keywords, table and column names
and `?`. The tests check that values with quotes (`O'Brien`, `Robert'); DROP TABLE user; --`)
round-trip safely and never appear in the SQL text.

## Part 4: comparing and showing

- `repr(User(name="Ann", age=30))` is `User(id=None, name='Ann', email=None, age=30)`.
- Two objects are equal when they are of the same model class and all field values are equal.

## Example session

```python
import sqlite3
conn = sqlite3.connect(":memory:")
User.create_table(conn)

ann = User(name="O'Brien", age=30).save(conn)   # ann.id == 1
User(name="Bob").save(conn)                     # id 2, age 18 (default), email NULL
User.get(conn, 1) == ann                        # True (a new, equal object)
User.filter(conn, email=None)                   # both users
User.filter(conn, name="' OR '1'='1")           # [] (it is just a strange name)
ann.age = "thirty"                              # TypeError: User.age must be int, got str
```

The tests are grouped by feature (`TestFieldDescriptors`, `TestModelDefinition`,
`TestCreateTable`, `TestSave`, `TestGet`, `TestFilter`, `TestDelete`,
`TestParameterisedQueries`, `TestReprAndEquality`). Work through them in that order with
`pytest -k TestFieldDescriptors` and so on.
