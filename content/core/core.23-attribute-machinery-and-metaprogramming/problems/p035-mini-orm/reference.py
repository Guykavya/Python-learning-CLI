class Field:
    """A validated column. Subclasses set sql_type and python_type."""

    sql_type = ""
    python_type = object

    def __init__(self, *, primary_key=False, null=False, default=None):
        self.primary_key = primary_key
        self.null = null
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, self.default)

    def __set__(self, obj, value):
        self.validate(value, type(obj).__name__)
        obj.__dict__[self.name] = value

    def validate(self, value, owner_name):
        where = f"{owner_name}.{self.name}"
        if value is None:
            if self.null or self.primary_key:
                return
            raise ValueError(f"{where} cannot be None")
        if not isinstance(value, self.python_type) or isinstance(value, bool):
            raise TypeError(f"{where} must be {self.python_type.__name__}, got {type(value).__name__}")

    def column_sql(self):
        sql = f"{self.name} {self.sql_type}"
        if self.primary_key:
            sql += " PRIMARY KEY"
        elif not self.null:
            sql += " NOT NULL"
        return sql


class IntegerField(Field):
    sql_type = "INTEGER"
    python_type = int


class TextField(Field):
    sql_type = "TEXT"
    python_type = str

    def __init__(self, *, max_length=None, **options):
        super().__init__(**options)
        self.max_length = max_length

    def validate(self, value, owner_name):
        super().validate(value, owner_name)
        if value is not None and self.max_length is not None and len(value) > self.max_length:
            raise ValueError(f"{owner_name}.{self.name} is longer than {self.max_length} characters")


class Model:
    _fields = {}          # name -> Field, in column order
    _pk = None            # name of the primary key field

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        fields = dict(cls._fields)                       # inherited fields first
        for name, value in vars(cls).items():            # then our own, in definition order
            if isinstance(value, Field):
                fields[name] = value
        keys = [name for name, field in fields.items() if field.primary_key]
        if len(keys) > 1:
            raise TypeError(f"{cls.__name__} has more than one primary key: {', '.join(keys)}")
        if not keys:
            if "id" in fields:
                raise TypeError(f"{cls.__name__}.id must be the primary key")
            pk = IntegerField(primary_key=True)
            pk.__set_name__(cls, "id")                   # not automatic after the class exists
            setattr(cls, "id", pk)
            fields = {"id": pk, **fields}
            keys = ["id"]
        cls._fields = fields
        cls._pk = keys[0]
        if "table_name" not in vars(cls):
            cls.table_name = cls.__name__.lower()
        if not isinstance(cls.table_name, str) or not cls.table_name.isidentifier():
            raise TypeError(f"{cls.__name__}.table_name must be a valid identifier")

    def __init__(self, **values):
        for name, value in values.items():
            if name not in self._fields:
                raise TypeError(f"{type(self).__name__} has no field {name!r}")
            setattr(self, name, value)

    # ----- helpers -----
    def _values(self):
        return {name: getattr(self, name) for name in self._fields}

    @classmethod
    def _from_row(cls, row):
        return cls(**dict(zip(cls._fields, row)))

    @classmethod
    def _select(cls):
        return f"SELECT {', '.join(cls._fields)} FROM {cls.table_name}"

    # ----- schema -----
    @classmethod
    def create_table_sql(cls):
        columns = ", ".join(field.column_sql() for field in cls._fields.values())
        return f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({columns})"

    @classmethod
    def create_table(cls, conn):
        conn.execute(cls.create_table_sql())

    # ----- writing -----
    def save(self, conn):
        values = self._values()
        for name, field in self._fields.items():
            if values[name] is None and not field.null and not field.primary_key:
                raise ValueError(f"{type(self).__name__}.{name} cannot be None")
        pk = self._pk
        others = [name for name in self._fields if name != pk]
        if values[pk] is not None:
            assignments = ", ".join(f"{name} = ?" for name in others)
            cursor = conn.execute(
                f"UPDATE {self.table_name} SET {assignments} WHERE {pk} = ?",
                [values[name] for name in others] + [values[pk]],
            )
            if cursor.rowcount == 0:
                self._insert(conn, [pk] + others, values)
            return self
        if not isinstance(self._fields[pk], IntegerField):
            raise ValueError(f"{type(self).__name__}.{pk} must be set before saving")
        cursor = self._insert(conn, others, values)
        setattr(self, pk, cursor.lastrowid)
        return self

    def _insert(self, conn, names, values):
        marks = ", ".join("?" for _ in names)
        return conn.execute(
            f"INSERT INTO {self.table_name} ({', '.join(names)}) VALUES ({marks})",
            [values[name] for name in names],
        )

    def delete(self, conn):
        pk_value = getattr(self, self._pk)
        if pk_value is None:
            raise ValueError(f"{type(self).__name__} was never saved")
        conn.execute(f"DELETE FROM {self.table_name} WHERE {self._pk} = ?", [pk_value])
        setattr(self, self._pk, None)

    # ----- reading -----
    @classmethod
    def get(cls, conn, pk_value):
        row = conn.execute(f"{cls._select()} WHERE {cls._pk} = ?", [pk_value]).fetchone()
        return None if row is None else cls._from_row(row)

    @classmethod
    def filter(cls, conn, **criteria):
        conditions, params = [], []
        for name, value in criteria.items():
            if name not in cls._fields:
                raise TypeError(f"{cls.__name__} has no field {name!r}")
            if value is None:
                conditions.append(f"{name} IS NULL")
            else:
                conditions.append(f"{name} = ?")
                params.append(value)
        sql = cls._select()
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += f" ORDER BY {cls._pk}"
        return [cls._from_row(row) for row in conn.execute(sql, params).fetchall()]

    # ----- comparing and showing -----
    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self._values() == other._values()

    def __repr__(self):
        inside = ", ".join(f"{name}={value!r}" for name, value in self._values().items())
        return f"{type(self).__name__}({inside})"
