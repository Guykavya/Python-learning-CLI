# The first revision

Chapter section 13.3. An Alembic **revision** is a Python file with two functions: `upgrade()` moves the database forward, `downgrade()` undoes it. In this course you write only the **bodies**, as two functions of `solution.py`; the tests build the revision file around them and run it with Alembic against a SQLite file.

```python
upgrade_0001()      # creates the table products
downgrade_0001()    # removes it again
```

`upgrade_0001` must create (with `alembic.op`, not with raw SQL strings):

```text
products(id INTEGER primary key, name VARCHAR(100) not null, price_paise INTEGER not null)
```

`downgrade_0001` must remove the table, so that after `downgrade base` the database has **no** `products` table (only Alembic's own `alembic_version` bookkeeping table).

## Example

```python
from alembic import op
import sqlalchemy as sa

def upgrade_0001():
    op.create_table("products", sa.Column("id", sa.Integer(), primary_key=True), ...)
```

Tests: `upgrade head` creates the table with the right columns and records the revision `0001`; `downgrade base` drops it.
