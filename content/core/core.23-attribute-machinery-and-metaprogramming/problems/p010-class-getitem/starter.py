class TypedList(list):
    item_type = object

    # TODO: __class_getitem__(cls, item_type) returning a cached subclass
    # TODO: __init__(self, items=()) and append(self, item) that check item types
