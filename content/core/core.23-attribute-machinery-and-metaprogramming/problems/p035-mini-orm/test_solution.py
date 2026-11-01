"""Mini ORM tests, grouped by feature. Run one group with: pytest -k TestSave"""

import sqlite3

import pytest

from solution import Field, IntegerField, Model, TextField


class User(Model):
    name = TextField(max_length=40)
    email = TextField(null=True)
    age = IntegerField(default=18)

    def greeting(self):
        return f"Hi {self.name}"


class Book(Model):
    table_name = "books"
    isbn = TextField(primary_key=True)
    title = TextField()
    pages = IntegerField(null=True)


class Admin(User):
    level = IntegerField(default=1)


class SpyConnection:
    """Wraps a real sqlite3 connection and records every (sql, params) passed to execute."""

    def __init__(self, real):
        self.real = real
        self.statements = []

    def execute(self, sql, params=()):
        self.statements.append((sql, tuple(params)))
        return self.real.execute(sql, params)

    def commit(self):
        self.real.commit()


@pytest.fixture
def conn():
    real = sqlite3.connect(":memory:")
    spy = SpyConnection(real)
    for model in (User, Book, Admin):
        model.create_table(spy)
    spy.statements.clear()
    yield spy
    real.close()


def count_rows(conn, table):
    return conn.real.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


# --------------------------------------------------------------------------- fields
class TestFieldDescriptors:
    def test_class_access_returns_the_field(self):
        assert isinstance(User.name, TextField), "User.name (no instance) must return the Field itself: if obj is None: return self."
        assert User.name.name == "name" and User.age.name == "age", "Each field learns its attribute name in __set_name__."
        assert issubclass(IntegerField, Field) and issubclass(TextField, Field), "IntegerField and TextField subclass Field."

    def test_defaults(self):
        u = User()
        assert u.age == 18, "A field that was never set returns its default."
        assert u.email is None and u.id is None, "The default default is None (id is None until the row is saved)."

    def test_values_are_per_instance(self):
        a, b = User(name="Ann"), User(name="Bob")
        assert (a.name, b.name) == ("Ann", "Bob"), (
            "Each instance needs its own value. Store it in obj.__dict__, not on the descriptor (one per class)."
        )
        assert a.__dict__["name"] == "Ann", "Store the value in the instance __dict__ under the field name."

    def test_type_validation_on_assignment(self):
        u = User(name="Ann")
        with pytest.raises(TypeError) as info:
            u.age = "old"
        assert "User.age" in str(info.value), "The TypeError message must name the field as 'User.age'."
        with pytest.raises(TypeError):
            u.age = True
        with pytest.raises(TypeError):
            u.age = 3.5
        with pytest.raises(TypeError) as info:
            u.name = 42
        assert "User.name" in str(info.value), "TextField accepts only str."
        assert (u.age, u.name) == (18, "Ann"), "A rejected value must not be stored."

    def test_bool_is_not_an_integer_here(self):
        with pytest.raises(TypeError):
            User(name="Ann", age=False)

    def test_none_and_null(self):
        u = User(name="Ann")
        with pytest.raises(ValueError) as info:
            u.name = None
        assert "User.name" in str(info.value), "None in a field without null=True raises ValueError naming the field."
        u.email = None
        u.id = None
        assert u.email is None and u.id is None, "null=True fields and the primary key accept None."

    def test_max_length(self):
        with pytest.raises(ValueError) as info:
            User(name="x" * 41)
        assert "User.name" in str(info.value), "TextField(max_length=40) rejects 41 characters with ValueError."
        assert User(name="x" * 40).name == "x" * 40, "Exactly max_length characters is allowed."

    def test_init_rejects_unknown_names(self):
        with pytest.raises(TypeError):
            User(nickname="Al")
        with pytest.raises(TypeError):
            User(greeting="hi")


# ------------------------------------------------------------------ model definition
class TestModelDefinition:
    def test_fields_in_definition_order_with_automatic_id(self):
        assert list(User._fields) == ["id", "name", "email", "age"], (
            "A model without a primary key gets id = IntegerField(primary_key=True) FIRST, then its fields in definition order."
        )
        assert User._pk == "id", "_pk names the primary key field."
        assert isinstance(vars(User)["id"], IntegerField) and User.id.primary_key, "The automatic id is a real IntegerField on the class."
        assert User.id.name == "id", (
            "Setting a descriptor on a class after creation does NOT call __set_name__: call it yourself for the automatic id."
        )
        assert all(isinstance(f, Field) for f in User._fields.values()), "_fields maps names to Field objects."

    def test_explicit_primary_key(self):
        assert list(Book._fields) == ["isbn", "title", "pages"], "A model with its own primary key gets no automatic id."
        assert Book._pk == "isbn" and "id" not in vars(Book), "Book's primary key is isbn."

    def test_table_names(self):
        assert User.table_name == "user", "Default table_name is the class name in lower case."
        assert Book.table_name == "books", "An explicit table_name is kept."
        assert Admin.table_name == "admin", (
            "A subclass gets its own default table name. Check 'table_name' in vars(cls), not hasattr (which sees the parent's)."
        )

    def test_inheritance(self):
        assert list(Admin._fields) == ["id", "name", "email", "age", "level"], (
            "A subclass model keeps the parent's fields (first) and adds its own."
        )
        assert list(User._fields) == ["id", "name", "email", "age"], "Creating a subclass must not change the parent's fields."
        assert Admin(name="Root").greeting() == "Hi Root", "Methods are inherited and are not fields."

    def test_two_primary_keys_rejected(self):
        with pytest.raises(TypeError):
            class Bad(Model):
                a = IntegerField(primary_key=True)
                b = TextField(primary_key=True)

    def test_table_name_must_be_an_identifier(self):
        with pytest.raises(TypeError):
            class Evil(Model):
                table_name = "x; DROP TABLE user"
                name = TextField()

    def test_fields_found_without_annotations(self):
        class Plain(Model):
            title = TextField()
            stars = IntegerField(default=0)

        class Annotated(Model):
            title: str = TextField()
            note: str = "not a field"

        assert list(Plain._fields) == ["id", "title", "stars"], (
            "Fields are discovered by scanning vars(cls) for Field objects (or via __set_name__), not from __annotations__."
        )
        assert list(Annotated._fields) == ["id", "title"], "An annotated plain value is not a field."


# --------------------------------------------------------------------- create table
class TestCreateTable:
    def test_sql_text(self):
        assert User.create_table_sql() == (
            "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, age INTEGER NOT NULL)"
        ), "Columns in field order: 'name TYPE', plus ' PRIMARY KEY' for the key, or ' NOT NULL' when null is False."
        assert Book.create_table_sql() == (
            "CREATE TABLE IF NOT EXISTS books (isbn TEXT PRIMARY KEY, title TEXT NOT NULL, pages INTEGER)"
        ), "The primary key column gets PRIMARY KEY and no NOT NULL."

    def test_tables_exist(self, conn):
        cols = [row[1] for row in conn.real.execute("PRAGMA table_info(admin)")]
        assert cols == ["id", "name", "email", "age", "level"], "create_table(conn) must execute create_table_sql()."
        User.create_table(conn)
        assert count_rows(conn, "user") == 0, "Running create_table twice must not fail (IF NOT EXISTS)."


# ----------------------------------------------------------------------------- save
class TestSave:
    def test_insert_sets_the_primary_key(self, conn):
        ann = User(name="Ann", age=30)
        assert ann.save(conn) is ann, "save returns self, so calls can be chained."
        bob = User(name="Bob").save(conn)
        assert (ann.id, bob.id) == (1, 2), "After an INSERT, set the primary key from cursor.lastrowid."
        row = conn.real.execute("SELECT name, email, age FROM user WHERE id = 2").fetchone()
        assert row == ("Bob", None, 18), "Defaults are saved too: age 18, email NULL."

    def test_update_existing_row(self, conn):
        ann = User(name="Ann", age=30).save(conn)
        ann.age = 31
        ann.email = "ann@example.com"
        ann.save(conn)
        assert count_rows(conn, "user") == 1, "Saving an object that already has an id must UPDATE, not INSERT a second row."
        assert conn.statements[-1][0].startswith("UPDATE user"), "The second save must run an UPDATE ... WHERE id = ?."
        row = conn.real.execute("SELECT age, email FROM user WHERE id = ?", (ann.id,)).fetchone()
        assert row == (31, "ann@example.com"), "UPDATE must write every non-key column."

    def test_new_object_with_explicit_id_is_inserted(self, conn):
        cy = User(id=10, name="Cy").save(conn)
        assert cy.id == 10 and count_rows(conn, "user") == 1, (
            "If UPDATE changed no row (cursor.rowcount == 0), INSERT the row including its primary key."
        )
        assert User.get(conn, 10) == cy, "The row must be stored under id 10."

    def test_text_primary_key(self, conn):
        book = Book(isbn="978-0", title="Python").save(conn)
        book.pages = 300
        book.save(conn)
        assert count_rows(conn, "books") == 1, "First save inserts (no row yet), second save updates."
        assert conn.real.execute("SELECT pages FROM books").fetchone() == (300,), "The update must be stored."
        with pytest.raises(ValueError):
            Book(title="No key").save(conn)

    def test_missing_required_value(self, conn):
        with pytest.raises(ValueError) as info:
            User().save(conn)
        assert "User.name" in str(info.value), "Saving with a required field still None raises ValueError naming it."
        assert count_rows(conn, "user") == 0, "Validate before running any SQL: nothing may be inserted."

    def test_subclass_saves_in_its_own_table(self, conn):
        root = Admin(name="Root", level=9).save(conn)
        assert count_rows(conn, "admin") == 1 and count_rows(conn, "user") == 0, "Admin rows go into the admin table."
        assert Admin.get(conn, root.id).level == 9, "The subclass's own field is saved."


# ------------------------------------------------------------------------------ get
class TestGet:
    def test_get_returns_an_equal_new_object(self, conn):
        ann = User(name="Ann", email=None, age=30).save(conn)
        loaded = User.get(conn, ann.id)
        assert type(loaded) is User, "get returns an instance of the model class."
        assert loaded == ann and loaded is not ann, "get builds a new object with the same values."
        assert (loaded.id, loaded.name, loaded.email, loaded.age) == (1, "Ann", None, 30), "Every column is loaded."

    def test_get_missing_returns_none(self, conn):
        assert User.get(conn, 99) is None, "get returns None when no row has that primary key."

    def test_get_with_text_key(self, conn):
        Book(isbn="978-1", title="Fluent").save(conn)
        assert Book.get(conn, "978-1").title == "Fluent", "get uses the model's own primary key column."


# --------------------------------------------------------------------------- filter
class TestFilter:
    @pytest.fixture
    def people(self, conn):
        rows = [("Ann", 30, "a@x"), ("Bob", 25, None), ("Cy", 30, None), ("Ann", 41, "a2@x")]
        return [User(name=n, age=a, email=e).save(conn) for n, a, e in rows]

    def test_one_and_two_criteria(self, conn, people):
        assert [u.id for u in User.filter(conn, age=30)] == [1, 3], "filter(conn, age=30) returns matching rows ordered by primary key."
        assert [u.id for u in User.filter(conn, name="Ann", age=41)] == [4], "Several criteria are joined with AND."
        assert all(type(u) is User for u in User.filter(conn, age=30)), "filter returns model instances."

    def test_no_criteria_returns_all(self, conn, people):
        assert [u.name for u in User.filter(conn)] == ["Ann", "Bob", "Cy", "Ann"], "filter with no criteria returns every row."

    def test_none_means_is_null(self, conn, people):
        assert [u.name for u in User.filter(conn, email=None)] == ["Bob", "Cy"], (
            "In SQL 'email = NULL' never matches. For None, generate 'email IS NULL' (with no parameter)."
        )

    def test_no_match(self, conn, people):
        assert User.filter(conn, name="Zed") == [], "No matching rows: an empty list."

    def test_unknown_field_rejected(self, conn, people):
        with pytest.raises(TypeError):
            User.filter(conn, nickname="Al")
        with pytest.raises(TypeError):
            User.filter(conn, **{"1=1 OR name": "x"})


# --------------------------------------------------------------------------- delete
class TestDelete:
    def test_delete(self, conn):
        ann = User(name="Ann").save(conn)
        User(name="Bob").save(conn)
        ann.delete(conn)
        assert count_rows(conn, "user") == 1 and User.get(conn, 1) is None, "delete removes exactly this row."
        assert ann.id is None, "After delete, the object's primary key is None (it is not in the table any more)."
        ann.save(conn)
        assert ann.id == 3 and count_rows(conn, "user") == 2, "Saving a deleted object inserts it again with a new id."

    def test_delete_unsaved(self, conn):
        with pytest.raises(ValueError):
            User(name="Ghost").delete(conn)


# ------------------------------------------------------------------ parameterised SQL
class TestParameterisedQueries:
    TRICKY = ["O'Brien", "Robert'); DROP TABLE user; --", "' OR '1'='1", 'say "hi"']

    def test_tricky_values_round_trip(self, conn):
        saved = [User(name=name, email=name).save(conn) for name in self.TRICKY]
        for user in saved:
            assert User.get(conn, user.id) == user, f"{user.name!r} must come back unchanged: pass values as ? parameters."
        assert count_rows(conn, "user") == len(self.TRICKY), "The table must still exist with every row (no injection)."
        assert [u.id for u in User.filter(conn, name="O'Brien")] == [1], "filter must find a value that contains a quote."

    def test_injection_in_filter_matches_nothing(self, conn):
        User(name="Ann").save(conn)
        User(name="Bob").save(conn)
        assert User.filter(conn, name="' OR '1'='1") == [], (
            "A value pasted into the SQL text would turn into OR '1'='1' and return every row. Use ? placeholders."
        )
        tricky = User(name="Bob").save(conn)
        tricky.name = "x' WHERE 1=1; --"
        tricky.save(conn)
        assert [u.name for u in User.filter(conn)] == ["Ann", "Bob", "x' WHERE 1=1; --"], (
            "An UPDATE with a value in the SQL text could change every row. Only this row may change."
        )

    def test_values_never_appear_in_sql_text(self, conn):
        ann = User(name="O'Brien", email="x'); DROP TABLE user; --", age=33).save(conn)
        ann.age = 34
        ann.save(conn)
        User.get(conn, ann.id)
        User.filter(conn, name="O'Brien", age=34)
        User.filter(conn, email=None)
        Book(isbn="q'1", title="T").save(conn)
        Book.get(conn, "q'1")
        ann.delete(conn)
        assert conn.statements, "Use conn.execute(sql, params) for every query."
        for sql, params in conn.statements:
            assert "'" not in sql, f"No quote may appear in the SQL text; values go in params. Got: {sql}"
            assert sql.count("?") == len(params), f"Every value needs exactly one ? placeholder. Got {sql!r} with {params!r}"
            assert "O'Brien" not in sql and "34" not in sql, f"Values must not be formatted into the SQL: {sql}"


# ------------------------------------------------------------------- repr and equality
class TestReprAndEquality:
    def test_repr(self):
        assert repr(User(name="Ann", age=30)) == "User(id=None, name='Ann', email=None, age=30)", (
            "repr lists every field in order as name=value!r."
        )

    def test_equality(self):
        assert User(name="Ann") == User(name="Ann"), "Two objects of the same model with equal field values are equal."
        assert User(name="Ann") != User(name="Bob"), "Different values: not equal."
        assert User(name="Ann") != Admin(name="Ann"), "Objects of different model classes are never equal."
