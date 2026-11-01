class TypedList(list):
    item_type = object
    _cache = {}

    def __class_getitem__(cls, item_type):
        if not isinstance(item_type, type):
            raise TypeError(f"TypedList[...] needs a class, got {item_type!r}")
        if item_type not in TypedList._cache:
            name = f"TypedList[{item_type.__name__}]"
            sub = type(name, (TypedList,), {"item_type": item_type})
            TypedList._cache[item_type] = sub
        return TypedList._cache[item_type]

    def _check(self, item):
        if not isinstance(item, self.item_type):
            raise TypeError(
                f"{type(self).__name__} expects {self.item_type.__name__}, got {type(item).__name__}"
            )

    def __init__(self, items=()):
        items = list(items)          # read a generator only once
        for item in items:
            self._check(item)
        super().__init__(items)

    def append(self, item):
        self._check(item)
        super().append(item)
