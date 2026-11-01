class Field:
    """A validated column. Subclasses set sql_type and python_type."""

    sql_type = ""
    python_type = object

    def __init__(self, *, primary_key=False, null=False, default=None):
        self.primary_key = primary_key
        self.null = null
        self.default = default
        self.name = None

    # TODO: __set_name__, __get__, __set__ (validate on every assignment), column_sql()


class IntegerField(Field):
    sql_type = "INTEGER"
    python_type = int


class TextField(Field):
    sql_type = "TEXT"
    python_type = str

    def __init__(self, *, max_length=None, **options):
        super().__init__(**options)
        self.max_length = max_length


class Model:
    _fields = {}          # name -> Field, in column order
    _pk = None            # name of the primary key field

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # TODO: collect fields, add the automatic id, set _pk and table_name

    def __init__(self, **values):
        raise NotImplementedError

    @classmethod
    def create_table_sql(cls):
        raise NotImplementedError

    @classmethod
    def create_table(cls, conn):
        raise NotImplementedError

    def save(self, conn):
        raise NotImplementedError

    def delete(self, conn):
        raise NotImplementedError

    @classmethod
    def get(cls, conn, pk_value):
        raise NotImplementedError

    @classmethod
    def filter(cls, conn, **criteria):
        raise NotImplementedError
