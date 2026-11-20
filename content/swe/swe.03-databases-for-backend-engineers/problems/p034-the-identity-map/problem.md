# The identity map

Chapter section 9.4. A `Session` keeps an **identity map**: one Python object per database row (per primary key), for as long as the session lives. Reading the same row again returns the **same object**, without a query. Another session has its own map. `expire` and `commit` mark objects as stale, so the next attribute access reloads them.

```python
from sqlalchemy import String, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
with Session(engine) as setup:
    setup.add(Customer(id=1, name="Asha"))
    setup.commit()

statements = []
event.listen(engine, "before_cursor_execute", lambda conn, cur, stmt, params, ctx, many: statements.append(stmt))

s1, s2 = Session(engine), Session(engine)

a = s1.get(Customer, 1)
print("1: queries =", len(statements))

statements.clear()
b = s1.get(Customer, 1)
print("2: same =", a is b, "queries =", len(statements))

statements.clear()
c = s2.get(Customer, 1)
print("3: same =", a is c, "queries =", len(statements))

statements.clear()
s1.expire(a)
name = a.name
print("4: same =", a is b, "queries =", len(statements))

statements.clear()
s1.commit()
name = a.name
print("5: queries =", len(statements))

statements.clear()
d = s1.get(Customer, 1)
print("6: same =", d is a, "queries =", len(statements))
```

Predict **exactly** what the six lines print. `queries` is the number of SQL statements the engine received during that step (the statements are cleared before each step). `a is b` prints `True` or `False`. Do not run it.

Write your answer in `answer.txt`, one printed line per line.

## How to work

1. Step 1: first read of the row in session `s1`: how many statements?
2. Step 2: a second `get` of the same primary key in `s1`: is a query needed? Is the object the same?
3. Step 3: a different session `s2`: does it share the identity map?
4. Step 4: `expire(a)` marks the object stale. Does `s1.expire` run a query? When does the query happen?
5. Step 5: `commit()` expires **all** objects of the session by default; step 6 reads again.

## After you answer

1. Why does step 6 need no query although the session was committed just before?
2. What would happen to the object `a` if another session changed the row's name between steps 2 and 4?
3. What does `expire_on_commit=False` change?
