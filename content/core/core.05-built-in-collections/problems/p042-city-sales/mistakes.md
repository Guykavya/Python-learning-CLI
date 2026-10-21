- `sales.get(city, {})[item] = ...`. `get` does not store the new inner dict, so the sale is lost.
- Creating one shared inner dict for every city (for example with `dict.fromkeys(cities, {})`):
  all cities would show the same items.
- Forgetting the two-space indent.
